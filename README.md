# skybeard v2.0

A plug-in based telegram bot 


## Installation
It is recommended to use a `virtualenv` for Skybeard. Create and activate the virtual environment with
```
virtualenv venv
source venv/bin/activate
```
then install the base requirements with
```
pip install -r requirements.txt
```

## Running Skybeard

To run skybeard define your key in the environment variable `$tg_bot_token` and run `main.py`. this can be done easily e.g.:

    TG_BOT_TOKEN=99121185:RUE-UAa7dsEaagAKkysPDjqa2X7KxX48e ./main.py

## Skybeard's Many Beards
Skybeard wears many beards. The bot will automatically load any "beard" (a plug-in) that is placed in the beards folder. Beards are structured like so:

```
beards
|
|___myPlugin
    |    __init__.py
    |    config.py
    |    requirements.txt
    |    ...
    |
    |___docs
        |    README
        |    ...
```
The `myPlugin` folder containts a `requirements.txt` for any additonal dependencies so they can be pipped, a `config.py` file for user specific variables (e.g private API keys) and settings and the `__init__.py` which contains the plugin class that must inheret from `plugins.Plugin`.
The folder can also contain any other python modules and files that are needed for the plugin, but Skybeard interfaces only with the Plugin class in `__init.py__`, allowing you to separate out the beard's logic from the interface.


    `

