#!/bin/bash

if [ "$1" != 'prod' ]; then
    export FLASK_ENV="development"
fi

# dirty hack to make it switch between plugin python3 and python
if [ -e "/usr/lib/uwsgi/python_plugin.so" ]; then
    plugin_name="python"
else
    plugin_name="python3"
fi

uwsgi --plugin ${plugin_name} -H./venv/ \
    --wsgi-file wsgi.py --callable application \
    --static-map /static=./public_html \
    --http-socket localhost:5000
