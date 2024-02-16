RECAPSE Web Application
======

Initial setup 
===
If setting up as a python application, create a virtualenv:

    python -m venv env

Then activate it:

    source env/bin/activate

Then install the required dependencies using pip:

    pip install -r requirements.txt

Running as a standalone application
===
To start the web application, execute `flask run`. This will start up a process listening on port 5000.

Running as a docker container
===
To start the docker container, run `docker run -d kcr/recapse-api:latest`
