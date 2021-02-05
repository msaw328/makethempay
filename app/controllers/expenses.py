from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
import psycopg2

# internals
from ..models import expenses as expensesmodel
from ..models import debts
from ..models import membership
from ..utils import login
from . import is_json_request_valid
from ..models import commit_transaction, rollback_transaction

# basic Blueprint router to which routes will be attached
router = Blueprint('expenses', __name__, template_folder='../views')

# UI routes, view-based
@router.route('/dashboard', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_dashboard():
    return render_template('/expenses/dashboard.jinja2')

@router.route('/group', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_group():
    return render_template('/expenses/group.jinja2')

# API routes, accept and return JSON
@router.route('/api/ingroup/<int:group_id>/create', methods=['POST'])
def api_create_expense(group_id):
    user_id = session['user_data']['id']    # COULD NOT WORK BECAUSE OF NOT BEING LOGGED IN

    # Check if user is in group
    try:
        user_is_in_group = membership.if_user_in_group(user_id, group_id)
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    if not user_is_in_group:
        return jsonify({
            'success': False,
            'error': 'This user does not have access to this group'
        })

    
    # EXAMPLE JSON:
    # "creditor_id": int,
    # "name": str,
    # "description": str,
    # "debtors": [
    #     {"debtor_id": 1,
    #     "amount_owed": 100.21
    #     },
    #     {"debtor_id": 2,
    #     "amount_owed": 120.21
    #     },
    #     {"debtor_id": 3,
    #     "amount_owed": 18.21
    #     }
    # ]
    
    req_check = is_json_request_valid(request, {
        # EXPENSES:
        'creditor_id': int,
        'name': str,
        'debtors': list
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    creditor_id = request.json['creditor_id']
    name = request.json['name']
    debtors = request.json['debtors']

    # Check if debtors list is valid:
    if not debtors.is_json:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters in debtors list'
        })

    for debtor in debtors:
        if not debtor['debtor_id'] in debtor or not isinstance(debtor['debtor_id'], int):
            return jsonify({
                'success': False,
                'error': 'Missing parameters or wrong type of parameters in debtors list'
            })
        if not debtor['amount_owed'] in debtor or not isinstance(debtor['amount_owed'], float):
            return jsonify({
                'success': False,
                'error': 'Missing parameters or wrong type of parameters in debtors list'
            })

    # Check if descritpion of expense exists
    if 'description' in request.json and isinstance(request.json['description'], str):
        description = request.json['description']
    else:
        description = None

    try:
        expense_data = expensesmodel.create(creditor_id, name, description)
        expense_id = expense_data['id']
        for debtor in debtors:
            debts.create(
                expense_id,
                debtor['debtor_id'],
                debtor['amount_owed']
                )
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    flash('Succesfully created new expense.')

    return jsonify({
        'success': True
    })

@router.route('/api/ingroup/<int:group_id>', methods=['GET'])
def api_get_expense(group_id):
    user_id = session['user_data']['id']    # COULD NOT WORK BECAUSE OF NOT BEING LOGGED IN

    # Check if user is in group
    try:
        user_is_in_group = membership.if_user_in_group(user_id, group_id)
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    if not user_is_in_group:
        return jsonify({
            'success': False,
            'error': 'This user does not have access to this group'
        })

    # If user is in group return expense
    try:
        data = expensesmodel.get_by_group_id(group_id)
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
        'result': data
    })
