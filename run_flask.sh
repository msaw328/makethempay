#!/bin/bash

if [ "$1" != 'prod' ]; then
    export FLASK_ENV="development"
fi

export FLASK_APP="app"

flask run
