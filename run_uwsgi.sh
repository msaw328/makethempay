#!/bin/bash

if [ "$1" != 'prod' ]; then
    export FLASK_ENV="development"
fi

uwsgi --plugin python --http localhost:5000 -H./venv/ --wsgi-file wsgi.py
