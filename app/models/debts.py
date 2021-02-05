from flask import g
import psycopg2

# DB debts table fields:
# id -> int
# expense_id -> int
# debtor_id -> int
# amount_paid -> float
# amount_owed -> float

# Creates new debt
def create(expense_id, debtor_id, amount_owed):
    query = """INSERT INTO debts (expense_id, debtor_id, amount_paid, amount_owed)
               VALUES (%(expense_id)s, %(debtor_id)s, 0, %(amount_owed)s)
               RETURNING *;
            """

    # INSERT INTO debts (expense_id, debtor_id, amount_paid, amount_owed) VALUES (1, 2, 0, 10) RETURNING *;

    params = {
        'expense_id': expense_id,
        'debtor_id': debtor_id,
        'amount_owed': amount_owedall
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows

# Changes amount_paid in debts
def update_amount_paid_by_id(debt_id, amount_paid):
    query = """UPDATE debts
               SET amount_paid = %(amount_paid)s
               WHERE id = %(debt_id)s
               RETURNING *;
               """

    # UPDATE debts SET amount_paid = %(amount_paid)s WHERE id = %(debt_id)s RETURNING *;

    params = {
        'amount_paid': amount_paid,
        'debt_id': debt_id
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows


# Gets debt with given expense_id
def get_by_expense_id(expense_id):
    query = """SELECT debtor_id, amount_paid, amount_owed
               FROM debts
               WHERE expense_id = %(expense_id)s;
               """

    # SELECT debtor_id, amount_paid, amount_owed FROM debts WHERE expense_id = %(expense_id)s;

    params = {
        'expense_id': expense_id
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchall()

    return returned_rows
