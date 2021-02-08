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

@router.route('/home', methods=['GET'])
# @login.required(goto='auth.ui_login')
def ui_home():
    return render_template('/membership/home.jinja2')

@router.route('/group/<int:group_id>', methods=['GET'])
def ui_show_group(group_id):
    return

@router.route('/group/new', methods=['GET'])
def ui_new_group():
    return render_template('/membership/new_group.jinja2')

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
        'user_display_name': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    if 'status' in request.json and isinstance(request.json['status'], str):
        status = request.json['status']
    else:
        status = None

    user_id = session['user_data']['id']
    access_token = request.json['access_token']
    user_display_name = request.json['user_display_name']

    # Validate token length
    if not len(access_token) == 31:
        return jsonify({
            'success': False,
            'error': 'Invalid token'
        })

    try:
        db_group = group.get_by_access_token(access_token)

        # If group with AccTkn does not exist
        if db_group is None:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'Group with this access token does not exist'
            })

        # Check if user is in the group
        is_user_in_group = member.is_user_in_group(user_id, db_group['id'])

        if is_user_in_group:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'User is already in the group'
            })

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

    if db_result is None:
        return jsonify({
            'success': False,
            'error': 'Can not add user into group. Please, validate your input'
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
        'group_display_name': str
    })

    if not req_check or not request.json['group_display_name'] or not request.json['user_display_name']:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    if 'status' in request.json and isinstance(request.json['status'], str):
        status = request.json['status']
    else:
        status = None

    if 'description' in request.json and isinstance(request.json['description'], str):
        description = request.json['status']
    else:
        description = None

    user_id = session['user_data']['id']
    user_display_name = request.json['user_display_name']
    group_display_name = request.json['group_display_name']
    access_token = generate_valid_token() 

    if access_token is None:
        return jsonify({
            'success': False,
            'error': 'Invalid token'
        })

    try:
        new_group = group.create(
            group_display_name,
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

# Update token function
@router.route('/api/updatetoken', methods=['POST'])
def api_update_token():
    req_check = is_json_request_valid(request, {
        'access_token': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    new_token = generate_valid_token() 
    old_token = request.json['access_token']

    if new_token is None:
        return jsonify({
            'success': False,
            'error': 'Invalid token'
        })

    try:
        db_result = group.update_token(
            new_token,
            old_token
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

# Validate if token exist and return token if unique
def generate_valid_token():
    old_token = ""

    while not old_token is None:
        new_token = gen_str()
        try:
            old_token = group.get_by_access_token(new_token)
        except psycopg2.Error as e:
            rollback_transaction()
            return None
        else:
            commit_transaction()

    return new_token
