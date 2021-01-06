from flask import Blueprint, render_template, jsonify, session, request, redirect
from passlib.hash import argon2
import re

# internals
from ..models import user as usermodel
from ..utils import is_json_request_valid

# basic Blueprint router to which routes will be attached
router = Blueprint('auth', __name__, template_folder='../views/auth')

# UI routes, view-based
@router.route('/register', methods=['GET'])
def ui_register():
    return render_template('register.jinja2')

@router.route('/login', methods=['GET'])
def ui_login():
    return render_template('login.jinja2')

@router.route('/secret', methods=['GET'])
def ui_secret():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/auth/login', code=302)

    return render_template('secret.jinja2')

# API routes, accept and return JSON
@router.route('/api/register', methods=['POST'])
def api_register():
    req_check = is_json_request_valid(request, {
        'email': str,
        'password': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    email = request.json['email']
    password = request.json['password']

    # also check if email has valid form
    # additionally we should send a verification email to fully validate it
    # https://stackoverflow.com/a/8022584
    EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    if not EMAIL_REGEX.fullmatch(email):
        return jsonify({
            'success': False,
            'error': 'Email address does not look like one (bad format)'
        })

    # check if user already exists with this email, should return None
    db_result = usermodel.find_by_email(email)

    if db_result is not None:
        return jsonify({
            'success': False,
            'error': 'User with this email already exists'
        })

    # at this point all checks have been performed, we can create a new user
    pw_hash = argon2.hash(password)

    usermodel.create(email, pw_hash)

    return jsonify({
        'success': True
    })

@router.route('/api/login', methods=['POST'])
def api_login():
    req_check = is_json_request_valid(request, {
        'email': str,
        'password': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    email = request.json['email']
    password = request.json['password']

    # unlike in api_register, this time we do want to actually find a user
    db_result = usermodel.find_by_email(email)

    if db_result is None:
        return jsonify({
            'success': False,
            'error': 'Wrong email or password'
        })

    is_pass_ok = argon2.verify(password, db_result['password_hash'])

    if not is_pass_ok:
        return jsonify({
            'success': False,
            'error': 'Wrong email or password'
        })

    # at this point we have authorized the user, log him in
    session['logged_in'] = True

    # cache some not-secret data in the session cookie
    session['user'] = {
        'id': db_result['id'],
        'email': email
    }

    return jsonify({
        'success': True
    })

@router.route('/api/logout', methods=['POST'])
def api_logout():
    session['logged_in'] = False
    session.pop('user', None)

    return jsonify({
        'success': True
    })
