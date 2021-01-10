from flask import g
import psycopg2

from . import run_single_query

# DB table fields:
# id -> int
# email_addr -> string
# password_hash -> string

# finds a user by email, returns entire row
def get_by_email(email):
    query = """SELECT * FROM users
               WHERE email_addr = %(email)s
               LIMIT 1;
               """
    
    params = {
        'email': email
    }

    err, rows = run_single_query(g.dbconn, query, params)

    if err is not None:
        return err, None

    if len(rows) > 0:
        return None, rows[0]

    return None, None

# creates a new user in the database and returns the row describing him
def create(email, pw_hash):
    query = """INSERT INTO users (email_addr, password_hash)
               VALUES (%(email)s, %(pw_hash)s)
               RETURNING *;
               """

    params = {
        'email': email,
        'pw_hash': pw_hash
    }

    err, rows = run_single_query(g.dbconn, query, params)

    if err is not None:
        return err, None

    return None, rows[0]
