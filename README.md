#MP4 converter
This is a simple app that converts mp4 files to csv. This only works for the mp4 styles specifically provided for this project
#Getting Started
##Prerequisitse
You need [node package manager][https://www.npmjs.com/] and pip, which should already be installed with python 3+
##Installing
Install the [virtual env][http://docs.python-guide.org/en/latest/dev/virtualenvs/] if needed then create the virtual environment at the top directory of the app. Then activate the virtual environment
>virtualenv my_app
>source my_app/bin/activate
Install the required python packages
>pip install -r requirements.txt
Install the javascript packages via npm
>npm install
Build the project
>webpack
Then export the flask app variable
>export FLASK_APP=webapp.py
Run the app with the following.
>flask run
