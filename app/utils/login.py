from flask import current_app, session, redirect, flash, url_for
from functools import wraps

# what it means to be logged in?
def is_logged_in():
    return 'is_logged_in' in session and session['is_logged_in'] == True

# decorater you can put on endpoint
# can specify route to go to if failed check
def required(goto, message='Please log in'):
    def _decorator(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            if not is_logged_in():
                flash(message)
                return redirect(url_for(goto), code=302)

            return f(*args, **kwargs)

        return _wrapped
    return _decorator

def do_login(user_obj):
    session['is_logged_in'] = True
    session['user_data'] = user_obj

def do_logout():
    session['is_logged_in'] = False
    session.pop('user_data', None)

def context_processor():
    return dict(is_logged_in=is_logged_in)
