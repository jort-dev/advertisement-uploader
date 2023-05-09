#!/usr/bin/env python3
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
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

delay = 0.1
timeout = 10
open_tabs = []
marktplaats_upload_url = "https://www.marktplaats.nl/plaats"
tweakers_login_url = "https://tweakers.net/my.tnet/login/"
tweakers_upload_url = "https://tweakers.net/aanbod/nieuw/aanbod/"


def printt(*argss, **kwargs):
    if args.verbose:
        to_print = " ".join(map(str, argss))
        print(to_print, **kwargs)


def select_dropdown(xpath, option_text):
    dropdown = driver.find_element(By.XPATH, xpath)
    center_element(dropdown)
    time.sleep(delay)
    select = Select(dropdown)
    select.select_by_visible_text(option_text)
    time.sleep(delay)


def sleep_until_url_change():
    try:
        url = driver.current_url
        while True:
            if url != driver.current_url:
                break
            time.sleep(1)
    except:
        traceback.print_exc()
        print(f"URL not changed but breaking because of above exception")


# only support for 2 tabs: 1 and 2
def switch_to_tab(tab_number):
    amount_of_tabs = len(driver.window_handles)
    printt(f"Switching to tab {tab_number}/{amount_of_tabs}")

    # opening tab whilst another page loads introduces a big delay
    WebDriverWait(driver, timeout).until(lambda x: driver.execute_script("return document.readyState") == "complete")

    # save the original tab reference
    if len(open_tabs) == 0:
        tab1_handle = driver.current_window_handle
        open_tabs.append(tab1_handle)

    # create the second tab if it does not exist
    if tab_number > 1 and amount_of_tabs == 1:
        print(f"Creating new tab")
        driver.switch_to.new_window('tab')
        WebDriverWait(driver, timeout).until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != open_tabs[0]:
                driver.switch_to.window(window_handle)
                open_tabs.append(window_handle)  # tab2_handle

    # switch tab
    if tab_number == 1:
        driver.switch_to.window(open_tabs[0])
    else:
        driver.switch_to.window(open_tabs[1])


def tab_and_get(url: str, tab_number: int):
    switch_to_tab(tab_number)
    driver.get(url)


def remove_hidden_attribute(xpath):
    printt(f"Removing hidden tag on element with xpath={xpath}")
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script(
        "arguments[0].removeAttribute('hidden')", element)


def center_element(element):
    driver.execute_script(
        "arguments[0].scrollIntoView({'block':'center','inline':'center'})", element)


def enter_field(xpath, text):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        if element is None:
            quit(f"Could not find element with {xpath} to enter {text}")
        center_element(element)
        time.sleep(delay)
        printt(f"Entering text in field: '{text}'")
        element.send_keys(text)
        time.sleep(delay)
    except Exception as e:
        traceback.print_exc()
        raise e


def click_button(xpath):
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        # element = driver.find_element(by=By.XPATH, value=xpath)
        if button is None:
            quit(f"Could not find button with {xpath} to click")
        center_element(button)
        time.sleep(delay)
        printt(f"Clicking button with xpath={xpath}")
        button.click()
        time.sleep(delay)
    except Exception as e:
        traceback.print_exc()
        raise e


def login_marktplaats(username, password):
    printt(f"Logging in to Marktplaats with {username}, {password}")
    cookie_button_xpath = '//*[@id="gdpr-consent-banner-accept-button"]'
    email_field_xpath = '//*[@id="email"]'
    password_field_xpath = '//*[@id="password"]'
    submit_button_xpath = '//*[@id="account-login-button"]'

    tab_and_get(marktplaats_upload_url, 1)
    click_button(cookie_button_xpath)
    enter_field(email_field_xpath, username)
    enter_field(password_field_xpath, password)
    click_button(submit_button_xpath)
    time.sleep(2)

    printt(f"Marktplaats logged in")


def login_tweakers(username, password):
    printt(f"Logging in to Tweakers with {username}, {password}")
    tab_and_get(tweakers_login_url, 2)
    username_xpath = '//*[@id="tweakers_login_form_user"]'
    password_xpath = '//*[@id="tweakers_login_form_password"]'
    enter_field(username_xpath, username)
    enter_field(password_xpath, password)
    time.sleep(delay)
    password_field = driver.find_element(By.XPATH, password_xpath)
    password_field.send_keys(Keys.ENTER)
    time.sleep(2)
    printt(f"Tweakers logged in")


def marktplaats_enter_title(title):
    title_field_xpath = '//*[@id="category-keywords"]'
    enter_field(title_field_xpath, title)

    find_category_button_xpath = '//*[@id="find-category"]'
    click_button(find_category_button_xpath)

    time.sleep(delay)
    submit_title_button_xpath = '//*[@id="category-selection-submit"]'
    click_button(submit_title_button_xpath)


def marktplaats_enter_description(description_text):
    description_iframe_xpath = '//*[@id="description_nl-NL_ifr"]'
    description_field_xpath = '//*[@id="tinymce"]'

    # wait for the description element to load, as it is within an iframe
    WebDriverWait(driver, timeout).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, description_iframe_xpath)))

    # wait for text field to load
    description_field = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, description_field_xpath)))

    # scroll to element (for user to see)
    center_element(description_field)
    time.sleep(delay)

    # enter description
    description_field.send_keys(description_text)

    # switch focus back from the iframe to the main frame
    driver.switch_to.default_content()
    time.sleep(delay)


def marktplaats_upload_photos(image_paths):
    upload_xpath = "//input[@tabindex = '-1']"
    count = 0
    for file_path in image_paths:
        count += 1
        printt(f"Uploading photo {count}/{len(image_paths)}: {file_path}")
        upload_elements = driver.find_elements(By.XPATH, upload_xpath)
        last_upload_element = upload_elements[-1]
        center_element(last_upload_element)
        last_upload_element.send_keys(file_path)
        # wait for next upload box to appear
        while True:
            if len(driver.find_elements(By.XPATH, upload_xpath)) > len(upload_elements):
                break
            time.sleep(0.1)


def tweakers_upload_photos(image_paths):
    upload_xpath = '//*[@id="advertisement_form_images"]/p[1]/input[1]'

    count = 0
    for file_path in image_paths:
        count += 1
        printt(f"Uploading photo {count}/{len(image_paths)}: {file_path}")
        enter_field(upload_xpath, file_path)


def upload_marktplaats(ad):
    printt(f"Placing advertisement on Marktplaats: {ad['title']}")
    tab_and_get(marktplaats_upload_url, 1)

    # title
    marktplaats_enter_title(ad['title'])

    # photos
    marktplaats_upload_photos(ad['image_paths'])

    # description
    marktplaats_enter_description(ad['description'])

    # price
    asking_price_xpath = '//*[@id="syi-bidding-price"]/input'
    enter_field(asking_price_xpath, ad['price'])

    # min price
    min_price_xpath = '//*[@id="syi-bidding-minimumprice"]/input'
    enter_field(min_price_xpath, ad['min_price'])

    # zip code
    zip_code_xpath = '//*[@id="postCode"]/input'
    enter_field(zip_code_xpath, ad['zip_code'])

    # delivery method
    delivery_method_xpath = '//*[@id="deliveryMethod"]/div/select'
    select_dropdown(delivery_method_xpath, "Ophalen")

    # advertisement plan
    plan_xpath = '//*[@id="js-bundle-FREE"]'
    remove_hidden_attribute(plan_xpath)
    click_button(plan_xpath)

    print(f"Verify the details and click upload to place the advertisement to Marktplaats.")
    sleep_until_url_change()

    print(f"Uploaded to Marktplaats!")
    time.sleep(delay)


def upload_tweakers(ad):
    printt(f"Placing advertisement on Tweakers: {ad['title']}")
    tab_and_get(tweakers_upload_url, 2)

    # category (user should configure this himself, too many options)
    category_xpath = '//*[@id="advertisement_form_relatedTweakbase_searchProduct"]'
    enter_field(category_xpath, ad['title'])

    # title
    title_xpath = '//*[@id="advertisement_form_title"]'
    enter_field(title_xpath, ad['title'])

    # description
    description_xpath = '//*[@id="advertisement_form_description"]'
    enter_field(description_xpath, ad['description'])

    # price
    price_xpath = '//*[@id="advertisement_form_price_price"]'
    enter_field(price_xpath, ad['price'])

    # state
    state_xpath = '//*[@id="advertisement_form_productState"]'
    select_dropdown(state_xpath, "gebruikssporen")

    # photos
    tweakers_upload_photos(ad["image_paths"])

    # zip code
    zip_code_xpath = '//*[@id="advertisement_form_address_postalCode"]'
    enter_field(zip_code_xpath, ad['zip_code'])

    # delivery cost
    delivery_costs_xpath = '//*[@id="advertisement_form_deliveryCosts"]'
    select_dropdown(delivery_costs_xpath, "Niet van toepassing")

    # delivery method
    delivery_methods_xpath = '//*[@id="advertisement_form_deliveryMethods_1"]'
    click_button(delivery_methods_xpath)  # checkbox

    # payment method
    payment_method_xpath = '//*[@id="advertisement_form_paymentOptions_7"]'
    click_button(payment_method_xpath)  # checkbox

    # allow reactions
    allow_reactions_xpath = '//*[@id="advertisement_form_allowResponses"]'
    click_button(allow_reactions_xpath)  # checkbox

    print(f"Verify the details and click upload to place the advertisement to Tweakers.")
    sleep_until_url_change()

    print(f"Uploaded to Tweakers!")


def assemble_advertisement_info(dir_path):
    ad = {}
    # find .txt file
    txt_files = [os.path.join(dir_path, x) for x in os.listdir(dir_path) if x.endswith(".txt")]
    if len(txt_files) != 1:
        quit(f"Expected 1 description .txt file but found {len(txt_files)}")

    # read .txt file
    with open(txt_files[0]) as file:
        file_lines = file.readlines()

    # title
    title = file_lines[0].strip()
    ad["title"] = title

    # price
    asking_price = file_lines[1].strip()
    if args.default_price != "":
        asking_price = args.default_price
    ad["price"] = asking_price

    # min price
    min_price = args.minimum_price
    if min_price == "":
        min_price = "0"
    ad["min_price"] = min_price

    # description text
    description_text = ""
    for line in file_lines[2:]:
        description_text += line
    description_text.strip()
    description_text += args.default_description  # append default description footer
    ad["description"] = description_text

    # zip code
    ad["zip_code"] = zip_code  # from args / file

    # folder path
    ad["dir_path"] = dir_path

    # image paths
    image_paths = []
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if not os.path.isfile(file_path):
            continue
        if any(substring in file_path.lower() for substring in (".jpg", ".png", ".jpeg")):
            image_paths.append(file_path)

    image_paths = natsorted(image_paths, key=lambda y: y.lower())  # sort items same as the file manager does
    ad["image_paths"] = image_paths

    printt(f"Parsed advertisement: {ad}")
    return ad


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
parser.add_argument("-p", "--default-price",
                    help="the price enter for the advertisements, ignoring the one defined in the description file",
                    type=str,
                    default=""
                    )
parser.add_argument("-d", "--default-description",
                    help="the text to append after the description of the advertisements",
                    type=str,
                    default=""
                    )
parser.add_argument("-m", "--minimum-price",
                    help="the minimum price to enter for the advertisements",
                    type=str,
                    default=""
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
parser.add_argument("-zc", "--zip_code",
                    help="your zip code, for example 1234AB",
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
zip_code = read_credential(
    credential_path="credentials/zip_code.txt",
    argument=args.zip_code
)


def get_driver():
    # instantiate chrome
    options = uc.ChromeOptions()
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )
    options.add_argument("--disable-notifications")  # not needed
    options.add_argument("--disable-popup-blocking")  # disable are you sure to leave this page? does not work
    options.set_capability('unhandledPromptBehavior', 'accept')  # default is dismiss, which confuses all the code

    driver = uc.Chrome(options=options)
    return driver


try:
    try:
        driver = get_driver()
        folder_paths = get_folder_paths()
        # login_marktplaats(marktplaats_username, marktplaats_password)
        login_tweakers(tweakers_username, tweakers_password)
        for folder_path in folder_paths:
            advertisement_info = assemble_advertisement_info(folder_path)
            # upload_marktplaats(advertisement_info)
            upload_tweakers(advertisement_info)

    except Exception as e:
        traceback.print_exc()

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
