from flask import g
import psycopg2

def create(display_name, access_token, description):

    query = """ INSERT INTO groups (display_name, access_token, description) 
                VALUES (%(display_name)s, %(access_token)s, %(description)s)
                RETURNING *;
            """

    # INSERT INTO groups (display_name, access_token, description) VALUES ('Nawiasy', 'xd', 'opisek') RETURNING *;

    params = {
        'display_name': display_name,
        'access_token': access_token,
        'description': description,
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows


# Get group by access token
def get_by_access_token(access_token):
    query = """
        SELECT *
        FROM groups
        WHERE access_token = %(access_token)s
        LIMIT 1;
    """

    params = {
        'access_token': access_token,
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows

# Set new token for existing group
def update_token(new_token, old_token):
    query = """
    UPDATE groups
    SET access_token = %(new_token)s 
    WHERE access_token = %(old_token)s
    RETURNING *;
    """

    params = {
        'new_token': new_token,
        'old_token': old_token
    }

    cursor = g.dbconn.cursor()
    cursor.execute(query, params)
    returned_rows = cursor.fetchone()

    return returned_rows
    