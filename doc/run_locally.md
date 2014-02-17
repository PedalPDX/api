Running Api Locally
===================

This instruction will allow you to run the API in a local environment.

Requirements
------------

* virtualenv

### Create a virtualenv
Run the script `./script/create-env` to initialize the virtual environment
with the current set of requirements.

### Start the Environment
To start the environment type `source ./venv/bin/activate` and notice that
your prompt includes the new `(venv)` label indicating that you are running
in a virtual environment. 

### Adding Packages
Once the environment is created you can use `pip install` to add python
modules to the environment. For example: `pip install fastkml` to install
the fast-kml library to the environment.

### Saving the installed packages
If you would like the environment to include the modules you have installed
in the virtual environment, run `pip freeze > requirements.txt`. This will
tell the virtual environment to install all of the packages the next time you
create the environment with `create-env`

### Leaving the virtual environment
To leave the virtual environment simply type `disable` at the prompt and you
will leave the virtual environment

## Running api
Once you have the `venv` folder from running `create-env`, and you have activated
the environment, you can continue starting the api with `python api.py`. `Ctrl-c`
to stop it.
