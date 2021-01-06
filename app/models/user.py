from flask import g

# DB table fields:
# id -> int
# email_addr -> string
# password_hash -> string

def find_by_email(email):
    conn = g.dbconn

    cursor = conn.cursor()

    query = """SELECT * FROM users
               WHERE email_addr = %(email)s
               LIMIT 1;
               """
    
    cursor.execute(query, {
        'email': email
        })

    record = cursor.fetchone()

    return record

def create(email, pw_hash):
    conn = g.dbconn

    cursor = conn.cursor()

    query = """INSERT INTO users (email_addr, password_hash)
               VALUES (%(email)s, %(pw_hash)s);
               """

    cursor.execute(query, {
        'email': email,
        'pw_hash': pw_hash
    })

    conn.commit()

    return
