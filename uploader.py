#!/usr/bin/env python3
"""
driver.find_element(By.XPATH, '//*[@id="html5_1gr6gtf1l1q4a11i15et1qan1lee4"]').send_keys('/home/jort/Pictures/cat_hole.jpg')
"""
import argparse
import os
import sys
import time
import traceback

import undetected_chromedriver as uc
import webview
from natsort import natsorted
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

delay = 1
marktplaats_upload_url = "https://www.marktplaats.nl/plaats"


def printt(*argss, **kwargs):
    if args.verbose:
        to_print = " ".join(map(str, argss))
        print(to_print, **kwargs)


def enter_field(xpath, text):
    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        if element is None:
            quit(f"Could not find element with {xpath} to enter {text}")
        printt(f"Entering {text}")
        element.send_keys(text)
        time.sleep(delay)
    except Exception as e:
        traceback.print_exc()
        raise e


def click_button(xpath):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        # element = driver.find_element(by=By.XPATH, value=xpath)
        if button is None:
            quit(f"Could not find button with {xpath} to click")
        printt(f"Clicking button.")
        button.click()
        time.sleep(delay)
    except Exception as e:
        traceback.print_exc()
        raise e


def login(username, password):
    printt(f"Logging in {username} with password {password}")
    cookie_button_xpath = '//*[@id="gdpr-consent-banner-accept-button"]'
    email_field_xpath = '//*[@id="email"]'
    password_field_xpath = '//*[@id="password"]'
    submit_button_xpath = '//*[@id="account-login-button"]'

    driver.get(marktplaats_upload_url)
    click_button(cookie_button_xpath)
    enter_field(email_field_xpath, username)
    enter_field(password_field_xpath, password)
    click_button(submit_button_xpath)

    printt(f"Were in.")


def enter_title(title):
    title_field_xpath = '//*[@id="category-keywords"]'
    enter_field(title_field_xpath, title)

    find_category_button_xpath = '//*[@id="find-category"]'
    click_button(find_category_button_xpath)

    time.sleep(1)
    submit_title_button_xpath = '//*[@id="category-selection-submit"]'
    click_button(submit_title_button_xpath)


def enter_description(description_text):
    time.sleep(1)
    body = driver.find_element(By.CSS_SELECTOR, "body")
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(delay)
    description_iframe_xpath = '//*[@id="description_nl-NL_ifr"]'
    description_field_xpath = '//*[@id="tinymce"]'
    WebDriverWait(driver, 5).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, description_iframe_xpath)))
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, description_field_xpath))).send_keys(description_text)
    driver.switch_to.default_content()  # switch back from the iframe to the main frame
    time.sleep(delay)
    body.send_keys(Keys.PAGE_UP)
    body.send_keys(Keys.PAGE_UP)


def upload_photos(dir_path):
    upload_xpath = "//input[@tabindex = '-1']"
    file_paths = []
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if not os.path.isfile(file_path):
            continue
        if not file_path.lower().endswith(".jpg"):
            continue
        file_paths.append(file_path)

    file_paths = natsorted(file_paths, key=lambda y: y.lower())  # sort items same as the file manager does
    printt(f"We have {len(file_paths)} images to upload.")

    count = 1
    for file_path in file_paths:
        printt(f"Uploading #{count}: {file_path}")
        last_upload_element = driver.find_elements(By.XPATH, upload_xpath)[-1]
        last_upload_element.send_keys(file_path)
        count += 1
        if count > 5:  # from here extra upload elements are generated which take more time
            time.sleep(2)
        else:
            time.sleep(1)


def place_advertisement(dir_path):
    printt(f"Placing advertisement from {dir_path}")
    driver.get(marktplaats_upload_url)
    txt_files = [os.path.join(dir_path, x) for x in os.listdir(dir_path) if x.endswith(".txt")]
    if len(txt_files) == 0:
        printt(f"No description found.")
        raise ValueError
    with open(txt_files[0]) as description_file:
        description_file_lines = description_file.readlines()

    title = description_file_lines[0].strip()

    description_text = ""
    for line in description_file_lines[1:]:
        description_text += line
    description_text.strip()

    enter_title(title)
    enter_description(description_text)
    upload_photos(dir_path)

    time.sleep(delay)
    body = driver.find_element(By.CSS_SELECTOR, "body")
    body.send_keys(Keys.PAGE_DOWN)


def ask_folders():
    # returns None if no folder is choosen, otherwise a list of paths
    dir_paths = None

    def open_file_dialog(w):
        nonlocal dir_paths
        try:
            dir_paths = w.create_file_dialog(dialog_type=webview.FOLDER_DIALOG,
                                             allow_multiple=True,
                                             directory=os.getcwd()
                                             )
        except TypeError:
            pass  # user exited file dialog without picking
        finally:
            w.destroy()

    printt(f"Launching folder picker")
    window = webview.create_window("", hidden=True)
    webview.start(open_file_dialog, window)
    printt(f"You picked these folders: {dir_paths}")
    return dir_paths


def get_folder_paths():
    if not args.folder_paths or len(args.folder_paths) == 0:
        printt("No folders supplied as argument, launching folder picker")
        folder_paths = ask_folders()
        if not folder_paths:
            quit("You picked an invalid folder")

    else:
        folder_paths = args.folder_paths

    for folder_path in folder_paths:
        if not folder_path or not os.path.isdir(folder_path):
            quit("You picked an invalid folder")

    # sanitize trailing slashes
    folder_paths = [os.path.normpath(folder_path) for folder_path in folder_paths]

    if len(folder_paths) == 0:
        quit(f"No folders found at this depth level. Try lowering it.")
    print(f"Uploading items in folders: {folder_paths}")
    return folder_paths


def read_credential(argument=None, credential_path=None):
    if argument is not None and argument != "":
        credential = argument
        printt(f"Read credential '{credential}' from arguments")
        return credential

    if credential_path is None:
        quit(f"No credentials supplied.")

    if not os.path.exists(credential_path):
        credential_path = os.path.join(sys.path[0], credential_path)

    if not os.path.exists(credential_path):
        quit(f"Cannot find credential file on {credential_path}")

    with open(credential_path) as file:
        file_content = file.read()
    credential = file_content.strip()
    if not credential or credential == "":
        quit(f"Empty credential file: {credential_path}")
    printt(f"Read credential '{credential}' from {credential_path}")
    return credential


parser = argparse.ArgumentParser(
    prog="Advertisement uploader",
    description="Upload your advertisement to multiple sites.",
    epilog="Created by Jort: github.com/jort-dev")
parser.add_argument("-v", "--verbose",
                    help="prints more messages about the process",
                    action="store_true",
                    )
parser.add_argument("-mu", "--marktplaats-username",
                    help="your Marktplaats login",
                    type=str,
                    default=""
                    )
parser.add_argument("-mp", "--marktplaats-password",
                    help="your Marktplaats password",
                    type=str,
                    default=""
                    )
parser.add_argument("-tu", "--tweakers-username",
                    help="your Tweakers username",
                    type=str,
                    default=""
                    )
parser.add_argument("-tp", "--tweakers-password",
                    help="your Tweakers password",
                    type=str,
                    default=""
                    )
parser.add_argument("folder_paths",
                    nargs=argparse.REMAINDER,
                    help="the paths to the advertisement folder(s),"
                         " where each folder has a description.txt file and photos for the advertisement",
                    )
args = parser.parse_args()
printt(args)

# load sensitive information from local disk
marktplaats_username = read_credential(
    credential_path="credentials/marktplaats_username.txt",
    argument=args.marktplaats_username
)
marktplaats_password = read_credential(
    credential_path="credentials/marktplaats_password.txt",
    argument=args.marktplaats_password
)
tweakers_username = read_credential(
    credential_path="credentials/tweakers_username.txt",
    argument=args.tweakers_username
)
tweakers_password = read_credential(
    credential_path="credentials/tweakers_password.txt",
    argument=args.tweakers_password
)

# instantiate chrome
options = uc.ChromeOptions()
# options.add_argument("--password-store=basic") # adding this does not work with Marktplaats
options.add_experimental_option(
    "prefs",
    {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    },
)
options.add_argument("--disable-notifications")
driver = uc.Chrome(options=options)

try:
    try:
        login("business.jort@gmail.com", "zakenman^2")
        folder_paths = get_folder_paths()
        for folder_path in folder_paths:
            place_advertisement(folder_path)

    except Exception as e:
        traceback.print_exc()
        print(f"Failed to place.")

    print(f"Program finished.")
    while True:
        cmd = input("Enter: ")
        try:
            eval(cmd)
        except Exception as e:
            print(f"Exception: {e}")
            traceback.print_exc()
            count = 0
except KeyboardInterrupt:
    print(f"Program stopped manually.")
