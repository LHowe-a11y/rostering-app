# Dental Rostering Tool  
This is the web application I have created to fulfil the request from my example client, as a part of Task 3.




## Contents  
They'll go here




## How to host the web application yourself :)


### Clone the code locally.

On this GitHub repository's main page, GitHub handily demonstrates a variety of ways to do this, which you can see by pressing the green button marked "<> Code". Clone the repository to the folder/location of your choice using one of these methods.
> ###### Note: This method should in theory work on most operating systems. It has been tested in Windows 11. (MacOS w/ Apple Silicon is currently in testing.)

If the settings in rostering-app/.vscode/settings.json bother you, you can change or delete it to your heart's content. 


### Install dependencies.

If you don't do this, the site won't work. The project includes a uv.lock file and a pyproject.toml file. You can install the dependencies your own way, the way I prefer for packages is through uv, which you can do like this:

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Navigate to the directory of the cloned repo. Should be something along the lines of `something/something/where_you_cloned_the_repo_to/rostering-app`
3. Create a virtual environment with `uv venv`
4. Install packages with `uv sync`

If that method does not work, you could try navigating to the repo directory, and then running `pip install PACKAGE_NAME` for each package. The names needed are in pyproject.toml, but I'll list them here too:

- flask

**Python 3.11 is required for this project.** Please [install Python from the website](https://www.python.org/downloads/), or perhaps use `uv python list` to find the right version and copy-paste into `uv python install COPY_PASTED_VERSION_NAME`.


### Run the web app.

Run app.py in the main directory. `python app.py`


### Visit the website.

The website should be hosted at 127.0.0.1:5000. On Macs, this port is sometimes occupied. This will cause an error alonmg the lines of "port 5000 already in use". To fix this, disable 'AirPlay Receiver' in settings. The address should appear in the terminal after running app.py, if everything is working correctly. The message should look like this (it might have more information depending on the settings but should include at least this info):

    * Serving Flask app 'appname'
    * Debug mode: on/off
    * Running on http://127.0.0.1:5000

#### Congratulations! You have now successfully hosted and accessed the Dental Rostering Tool Web App.




## How to use the web app/rostering tool

guess. (this section is not written yet)
