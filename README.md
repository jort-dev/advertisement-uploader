# Advertisement uploader
A tool to upload your advertisements to multiple sites, like [Marktplaats](https://www.marktplaats.nl/) and [Tweakers](https://tweakers.net/aanbod/).  

Use cases:
* prevent manually entering the same advertisement information on multiple websites
* quickly reupload your advertisements, useful for example if they expire or you want them to be higher up in the search results

For each advertisement, the program expects a folder with photos and a text file for the description.

## Folder structure
You will need to create a folder for each advertisement you want to upload.  
Such a folder needs to contain the photos and the description for the advertisement.  
The description should be provided as a `.txt` file, and must contain the following:
* First line: advertisement title
* Second line: asking price
* Remaining lines: description

## Running
Activate the virtual environment you created (see the _Installing_ instructions below)   
Run the program with `python uploader.py`.  
The program asks for one or more folders which have the structure as defined above.  
Then it will then enter the details on the advertisement site.  
After entering, you review/edit the details and **press upload yourself**.  
The program will then continue to the next.

## Installing
Have the latest [Chrome browser](https://www.google.com/chrome/) installed.  
Have the latest [Python version](https://www.python.org/downloads/windows/) installed, with python.exe added to the PATH.  
Open the terminal in cloned folder and create a virtual Python environment called `venv` to prevent package issues:
```shell
python -m venv venv
```
Activate the created virtual environment:
```shell
venv\Scripts\activate
```
On Linux, you may need to have the following packages installed:
```shell
yay -S gobject-introspection 
```
Install the required Python packages:
```shell
pip install -r requirements.txt
```









