from flask import g
import psycopg2

# DB expenses table fields:
# id -> int
# creator_id -> int
# name -> string
# description -> string - can be null

# Creates new expense in expenses table
def create(creditor_id, name, description):
    query = """INSERT INTO expenses (creditor_id, name, description)
               VALUES (%(creditor_id)s, %(name)s, %(description)s)
               RETURNING *;
            """

    # INSERT INTO expenses (creditor_id, name, description) VALUES (1,  'picka', 'picka z dagrasso') RETURNING *;

    params = {
        'creditor_id': creditor_id,
        'name': name,
        'description': description,
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows


# Gets expense with given group_id 
def get_by_group_id(group_id):
    query = """SELECT e.creditor_id, e.name, e.description, m.user_display_name
               FROM expenses e
               JOIN memberships m ON e.creditor_id = m.id
               WHERE m.group_id = %(group_id)s;
            """

    # SELECT (e.creditor_id, e.name, e.description, m.user_display_name) FROM expenses e JOIN memberships m ON e.creditor_id = m.id WHERE m.group_id = 1;

    params = {
        'group_id': group_id
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchall()

    return returned_rows
