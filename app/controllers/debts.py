from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for, flash
import psycopg2

# internals
from ..models import expenses as expensesmodel
from ..models import debts as debtsmodel
from ..models import membership
from ..utils import login
from . import is_json_request_valid
from ..models import commit_transaction, rollback_transaction

# basic Blueprint router to which routes will be attached
router = Blueprint('debts', __name__, template_folder='../views')

# UI routes, view-based
@router.route('/debt', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_debt():
    return render_template('/debts/debt.jinja2')

# API routes, accept and return JSON
@router.route('/api/update', methods=['POST'])
def api_update_amount_paid(group_id):
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

    req_check = is_json_request_valid(request, {
        'debt_id': int,
        'amount_paid': float
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    debt_id = request.json['debt_id']
    amount_paid = request.json['amount_paid']

    try:
        # sprawdzić jeszcze czy paid <= owed
        debtsmodel.update_amount_paid_by_id(debt_id, amount_paid)
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    flash('Succesfully changed amount paid.')

    return jsonify({
        'success': True
    })


@router.route('/api/inexpense/<int:expense_id>', methods=['GET'])
def api_get_debts(expense_id):
    user_id = session['user_data']['id']    # COULD NOT WORK BECAUSE OF NOT BEING LOGGED IN

    
    # WZIĄĆ GROUP_ID Z EXPENSA I SPRAWDZIĆ, CZY USER MA DOSTĘP DO GRUPY JUŻ W TRY
    # If user is in group return debts
    try:
        data = debtsmodel.get_by_expense_id(expense_id)
        user_is_in_group = membership.if_user_in_group(user_id, group_id)
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
