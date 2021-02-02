from flask import g
import psycopg2

def create(user_display_name, access_token, description):

    query = """ INSERT INTO groups (display_name, access_token, description) 
                VALUES (%(user_display_name)s, %(access_token)s, %(description)s)
                RETURNING *;
            """
    params = {
        'user_display_name': user_display_name,
        'access_token': access_token,
        'description': description,
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows

def get_by_access_token(access_token):
    pass

"""
INSERT INTO groups (display_name, access_token, description) VALUES ('Nawiasy', 'xd', 'opisek') RETURNING *;
"""
