#!/usr/bin/env bash
# If the virtualenv is not populated, copy it over.
echo "Let's run skybeard!"
if [[ "$(ls -A ~/skybeard_virtualenv)" ]];
then
    :
else
    cp -r ~/skybeard_virtualenv_frozen/* ~/skybeard_virtualenv
fi
source ~/skybeard_virtualenv/bin/activate
cd code
pip install pip --upgrade
pip install .
skybeard
#python main.py
