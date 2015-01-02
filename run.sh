#!/bin/bash
export HOME=$('pwd')
export PYTHONPATH=$HOME
echo 'USERHOME: '$REAL_HOME
echo 'HOME: '$HOME
echo 'APPDATADIR: '$APPDATADIR
echo 'PYTHONPATH: '$PYTHONPATH
if [ ! -f games.json ] ; then
    echo 'games.json not found. will copy default...'
    cp default_games.json games.json
fi
if [ ! -f settings.json ] ; then
    echo 'settings.json not found. will copy default...'
    cp default_settings.json settings.json
fi

python $HOME/main.py
