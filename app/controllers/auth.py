from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
from passlib.hash import argon2
import re
import psycopg2

# internals
from ..models import user as usermodel
from ..models import membership as member
from ..utils import login
from ..models import commit_transaction, rollback_transaction
from . import is_json_request_valid

# basic Blueprint router to which routes will be attached
router = Blueprint('auth', __name__, template_folder='../views')

# UI routes, view-based
@router.route('/register', methods=['GET'])
def ui_register():
    return render_template('/auth/register.jinja2')

@router.route('/login', methods=['GET'])
def ui_login():
    return render_template('/auth/login.jinja2')

@router.route('/secret', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_secret():
    return render_template('/auth/secret.jinja2')

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
    try:
        db_result = usermodel.get_by_email(email)
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    if db_result is not None:
        return jsonify({
            'success': False,
            'error': 'User with this email already exists'
        })

    # at this point all checks have been performed, we can create a new user
    pw_hash = argon2.hash(password)

    try:
        usermodel.create(email, pw_hash)
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    flash('Succesfully registered. Use your credentials to log in.')

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
    try:
        db_result = usermodel.get_by_email(email)
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()
        
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

    # at this point we have authorized the user, log him in and cache his data
    login.do_login({
        'id': db_result['id'],
        'email': email
    })
    flash('Succesfully logged in')

    return jsonify({
        'success': True
    })

@router.route('/api/logout', methods=['POST'])
def api_logout():
    login.do_logout()
    flash('Succesfully logged out')

    return jsonify({
        'success': True
    })
