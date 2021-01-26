from flask import g
import psycopg2

# DB table fields:
# id -> int
# user_id -> int
# group_id -> int
# user_display_name -> string
# status -> string

# Gets user's group info
def get_by_user_id(user_id):
    query = """SELECT (m.id, m.user_id, m.group_id, m.user_display_name, m.status, g.display_name, g.access_token, g.description)
               FROM memberships m 
               JOIN groups g ON m.group_id = g.id 
               WHERE user_id=%(user_id)s;
               """

    params = {
        'user_id': user_id
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows

# Adds user into the group
def join(user_id, group_id, user_display_name, status):
    query = """ INSERT INTO memberships (user_id, group_id, user_display_name, status)
                VALUES (%(user_id)s, %(group_id)s, %(user_display_name)s, %(status)s)
                RETURNING *;
              """

    params = {
        'user_id': user_id,
        'group_id': group_id,
        'user_display_name': user_display_name,
        'status': status
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchall()

    return returned_rows
