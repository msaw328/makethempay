#!/bin/bash

if [ "$1" != 'prod' ]; then
    export FLASK_ENV="development"
fi

uwsgi --plugin python -H./venv/ \
    --wsgi-file wsgi.py --callable application \
    --static-map /static=./public_html \
    --http localhost:5000
