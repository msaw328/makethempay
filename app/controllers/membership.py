from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
import random
import string

# internals
from ..models import membership as member
from ..models import group
from ..utils import login
import psycopg2
from . import is_json_request_valid
from ..models import commit_transaction, rollback_transaction

# basic Blueprint router to which routes will be attached
router = Blueprint('member', __name__, template_folder='../views')

@router.route('/', methods=['GET'])
# @login.required(goto='auth.ui_login')
def ui_dashboard():
    return render_template('/membership/member.jinja2')

# Get user's groups
@router.route('/api/me/groups', methods=['GET'])
def api_member():    
    user_id = session['user_data']['id']
    try:
        db_result = member.get_by_user_id(user_id)
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
            'error': 'User does not exist'
        })

    return jsonify({
        'success': True,
        'result': db_result
    })

# Add user into existing group
@router.route('/api/join', methods=['POST'])
def api_add_member():
    req_check = is_json_request_valid(request, {
        'access_token': str,
        'user_display_name': str,
        'status': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })


    user_id = session['user_data']['id']
    access_token = request.json['access_token']
    user_display_name = request.json['user_display_name']
    status = request.json['status']

    # Valid token length
    if not len(access_token) == 31:
        return jsonify({
            'success': False,
            'error': 'Invalid token'
        })

    try:
        db_group = group.get_by_access_token(
            access_token
        )
        # If group with AccTkn exists
        if not db_group is None:
            db_result = member.join(
                user_id,
                db_group['id'],
                user_display_name,
                status
            )
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    if db_group is None:
        return jsonify({
            'success': False,
            'error': 'Group with this access token does not exist'
        })

    if db_result is None:
        return jsonify({
            'success': False,
            'error': 'Can not add user into group. Please, valid your input'
        })

    return jsonify({
        'success': True,
        'result': db_result
    })

# Create new group and add creator into it
@router.route('/api/create', methods=['POST'])
def api_create_add_member():
    req_check = is_json_request_valid(request, {
        'user_display_name': str,
        'status': str,
        'description': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    user_id = session['user_data']['id']
    user_display_name = request.json['user_display_name']
    status = request.json['status']
    access_token = generate_valid_token() 
    description = request.json['description']

    try:
        new_group = group.create(
            user_display_name,
            access_token,
            description
        )
        db_result = member.join(
            user_id,
            new_group["id"],
            user_display_name,
            status
        )
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    return jsonify({
        'success': True,
        'result': db_result
    })


# Generate random string
def gen_str():
    token_length = 31
    words_set = string.ascii_uppercase + string.ascii_lowercase + string.digits

    return ''.join(random.choice(words_set) for _ in range(token_length))

# Valid if token exist and return token if unique
def generate_valid_token():
    old_token = ""

    while not old_token is None:
        new_token = gen_str()
        try:
            old_token = group.get_by_access_token(new_token)
        except psycopg2.Error as e:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'Database error'
            })
        else:
            commit_transaction()

    return new_token
