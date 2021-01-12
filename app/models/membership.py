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
    query = """SELECT (m.id, m.user_id, m.group_id, m.user_display_name, m.status, g.display_name, g.access_token, g.description)
               FROM memberships m 
               JOIN groups g ON m.group_id = g.id 
               WHERE user_id=%(user_id)s;
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
# - USER_ID             to identify user
# - GROUP_ID            to identify group
# - USER_DISPLAY_NAME   to initialize user name inside group
# - STATUS              dunno why
# - ACCESS_TOKEN        to invite friends into group
# - DESCRIPTION         group title or goals


def create_group_and_join(user_id, group_id, user_display_name, status, access_token, description):

    query1 = """INSERT INTO groups (display_name, access_token, description) 
                VALUES (%(user_display_name)s, %(access_token)s, %(description)s);
                """
    query2 = """INSERT INTO memberships (user_id, group_id, user_display_name, status)
               VALUES (%(user_id)s, %(group_id)s, %(user_display_name)s, %(status)s)
               RETURNING *;
               """

    params1 = {
        'user_display_name': user_display_name,
        'access_token': access_token,
        'description': description,
    }

    params2 = {
        'user_id': user_id,
        'group_id': group_id,
        'user_display_name': user_display_name,
        'status': status
    }

    err, rows = run_transaction_query(
        g.dbconn, [query1, query2], [params1, params2])

    try:
        cursor.execute(query, params)
    except psycopg2.Error as e:
        conn.rollback()
        return e, None

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
        'group_id': group_id,
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
