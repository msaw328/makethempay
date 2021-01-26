from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash

# internals
from ..models import membership as member
from ..models import group
from ..utils import login
import psycopg2
from . import is_json_request_valid
from ..models import commit_transaction, rollback_transaction

# basic Blueprint router to which routes will be attached
router = Blueprint('member', __name__, template_folder='../views')


@router.route('/member', methods=['GET'])
def ui_member():
    return render_template('/membership/member.jinja2')


@router.route('/api/member/show', methods=['POST'])
def api_member():
    req_check = is_json_request_valid(request, {
        'user_id': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    user_id = request.json['user_id']

    try:
        db_result = member.get_by_user_id(int(user_id))
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
        'success': True
    })

@router.route('/api/member/add', methods=['POST'])
def api_add_member():
    req_check = is_json_request_valid(request, {
        'user_id': str,
        'group_id': str,
        'user_display_name': str,
        'status': str
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    user_id = request.json['user_id']
    group_id = request.json['group_id']
    user_display_name = request.json['user_display_name']
    status = request.json['status']

    try:
        db_result = member.join(
            int(user_id),
            int(group_id),
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
            'error': 'Can not add user into group. Please, valid your input'
        })

    return jsonify({
        'success': True
    })

@router.route('/api/member/create', methods=['POST'])
def api_create_add_member():
    req_check = is_json_request_valid(request, {
        'user_id': str,
        'user_display_name': str,
        'status': str,
        'access_token': str,
        'description': str,
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    user_id = request.json['user_id']
    user_display_name = request.json['user_display_name']
    status = request.json['status']
    access_token = request.json['access_token']
    description = request.json['description']

    try:
        new_group = groups.create(
            user_display_name,
            access_token,
            description
        )
        db_result = member.join(
            int(user_id),
            int(new_group["id"]),
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
        'success': True
    })
