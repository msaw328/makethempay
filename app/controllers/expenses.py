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

@router.route('/<int:expense_id>', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_expense(expense_id):
    return render_template('/expenses/expense.jinja2', expense_id = expense_id)

@router.route('/ingroup/<int:group_id>/create', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_new_expense(group_id):
    return render_template('/expenses/new.jinja2', group_id = group_id)

@router.route('/group/<int:group_id>', methods=['GET'])
@login.required(goto='auth.ui_login')
def ui_group_dashboard(group_id):
    return render_template('/expenses/group_dashboard.jinja2', group_id = group_id)

# API routes, accept and return JSON
@router.route('/api/ingroup/<int:group_id>/create', methods=['POST'])
@login.required_api()
def api_create_expense(group_id):
    user_id = session['user_data']['id']    # COULD NOT WORK BECAUSE OF NOT BEING LOGGED IN

    # Check if user is in group
    try:
        user_membership = membership.get_user_in_group(user_id, group_id)
        if user_membership is None:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'You do not have access to this group'
            })
        creditor_id = user_membership['id']
        members = membership.get_all_members(group_id)
    except psycopg2.Error as e:
        print(e)
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

    # WHAT WE HAVE:
    # "name": str,
    # "description": str,
    # "all_amount_owed": str
    # group_id z urla
    
    # WHAT WE EXPECTED TO HAVE:
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
        'name': str,
        'all_amount_owed': int
    })

    if not req_check:
        return jsonify({
            'success': False,
            'error': 'Missing parameters or wrong type of parameters'
        })

    name = request.json['name']
    all_amount_owed = request.json['all_amount_owed']

    # Check if expense has at least one debt
    # if len(debtors) < 1:
    #     return jsonify({
    #         'success': False,
    #         'error': 'You have to specify at least one debtor in the expense'
    #     })

    # for debtor in debtors:
    #     debtor_id_ok = 'debtor_id' in debtor and isinstance(debtor['debtor_id'], int)
    #     amount_owed_ok = 'amount_owed' in debtor and isinstance(debtor['amount_owed'], float)
    #     if not debtor_id_ok or not amount_owed_ok:
    #         return jsonify({
    #             'success': False,
    #             'error': 'Missing parameters or wrong type of parameters in debtors list'
    #         })

    # Check if descritpion of expense exists
    if 'description' in request.json and isinstance(request.json['description'], str):
        description = request.json['description']
    else:
        description = None

    part_amount = all_amount_owed // len(members)

    try:
        expense_data = expensesmodel.create(creditor_id, name, description)
        expense_id = expense_data['id']
        for member in members:
            debts.create(
                expense_id,
                member['id'],
                part_amount
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
@login.required_api()
def api_get_expenses(group_id):
    user_id = session['user_data']['id']    # COULD NOT WORK BECAUSE OF NOT BEING LOGGED IN

    # Check if user is in group
    try:
        user_membership = membership.get_user_in_group(user_id, group_id)
        if user_membership is None:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'You do not have access to this group'
            })
    except psycopg2.Error as e:
        rollback_transaction()
        return jsonify({
            'success': False,
            'error': 'Database error'
        })
    else:
        commit_transaction()

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


@router.route('/api/<int:expense_id>', methods=['GET'])
@login.required_api()
def api_get_expense_by_id(expense_id):
    user_id = session['user_data']['id']    # COULD NOT WORK BECAUSE OF NOT BEING LOGGED IN

    # If user is in group return expense
    try:
        data = expensesmodel.get_by_id(expense_id)
        group_id = expensesmodel.get_group_id(expense_id)
        if group_id == None:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'There is not expense with given id'
            })
        if membership.get_user_in_group(user_id, group_id) is None:
            rollback_transaction()
            return jsonify({
                'success': False,
                'error': 'This user does not have access to this group'
            })
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
