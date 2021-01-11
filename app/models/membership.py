from flask import g
import psycopg2

from . import run_single_query

# DB table fields:
# id -> int
# user_id -> int
# group_id -> int
# user_display_name -> string
# status -> string

# Get user's group info
def get_by_user_id(user_id):

    # TODO: Zjoinować tabelę grupy i wyświetlić też jej wartości
    # query = """SELECT * FROM memberships m LEFT JOIN groups g ON m.group_id = g.id where user_id=%(user_id)s;
    #            """
    query = """SELECT (id, user_id, groups_id, user_display_name, status, display_name as group_display_name, access_token, description)
               FROM memberships m LEFT JOIN groups g ON m.group_id = g.id where user_id=%(user_id)s;
               """
    # Jak ominąć kolumnę g.id? Fajnie jakby się zmergowała z kolumną m.group_id
    
    params = {
        'user_id': user_id
    }

    err, rows = run_single_query(g.dbconn, query, params)

    if err is not None:
        return err, None

    if len(rows) > 0:
        return None, rows

    return None, None

# Create group
def create_group_and_join(user_id, group_id, user_display_name, status):
    query = """INSERT INTO memberships (user_id, group_id, user_display_name, status)
               VALUES (%(user_id)s, %(group_id)s, %(user_display_name)s, %(status)s)
               RETURNING *;
               """

    params = {
        'user_id': user_id,
        'group_id': group_id
        'user_display_name': user_display_name,
        'status': status
    }

    err, rows = run_single_query(g.dbconn, query, params)

    if err is not None:
        return err, None

    return None, rows[0]

# Add user into existing group
def add_user_to_group(user_id, group_id, user_display_name, status):

    query = """INSERT INTO memberships (user_id, group_id, user_display_name, status)
               VALUES (%(user_id)s, %(group_id)s, %(user_display_name)s, %(status)s)
               RETURNING *;
               """

    params = {
        'user_id': user_id,
        'group_id': group_id
        'user_display_name': user_display_name,
        'status': status
    }

    err, rows = run_single_query(g.dbconn, query, params)

    if err is not None:
        return err, None

    return None, rows[0]

# # Usuwanie z grupy
# # Jeśli grupa jest pusta to delete grupe. Poszukać info
# def remove_from_group():
#     pass
