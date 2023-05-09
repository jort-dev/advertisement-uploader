# Advertisement uploader
A tool to upload your advertisements to multiple sites, like [Marktplaats](https://www.marktplaats.nl/) and [Tweakers](https://tweakers.net/aanbod/).  
It is useful if you don't want to manually upload the same information on multiple sites, or if you want to reupload your advertisements for them to be higher up in the search results.
For each advertisement, the program expects a folder with images and a description text file.

## Folder structure
For each advertisement you want to create, you need to create a folder.  
This folder needs to contain the images, in the order you want them to show in the advertisement.
The folder also must have a `.txt` file.  
This `.txt` file must contain the following:
* First line: advertisement title
* Second line: asking price
* Remaining lines: description

## Installing
Have the latest [Chrome browser](https://www.google.com/chrome/) installed.  
Have the latest [Python version](https://www.python.org/downloads/windows/) installed, with python.exe added to the PATH.  
Open the terminal in cloned folder and create a virtual Python environment called `venv` to prevent package issues:
```shell
python -m venv venv
```
Activate the created virtual environment:
```shell
. venv\Scripts\activate
```
On Linux, you need to have the following packages installed:
```shell
yay -S gobject-introspection 
```
Install the required Python packages:
```shell
pip install -r requirements.txt
```

## Running
Open the terminal in the cloned folder and activate the created virtual environment:
```shell
. venv\Scripts\activate
```
Run the script
```shell
python uploader.py
```
The script will now run, and asks for one or more folders which have the structure as defined above.




