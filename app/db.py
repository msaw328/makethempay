import psycopg2
from psycopg2.extras import RealDictCursor

from flask import g, current_app

# stuff used to init flask app with our db
def _open_db():
    if 'dbconn' not in g:
        g.dbconn = psycopg2.connect(current_app.config['DB_CONN_STR'], cursor_factory=RealDictCursor)
        g.dbconn.autocommit = False

def _close_db(e):
    dbconn = g.pop('dbconn', None)
    if dbconn is not None:
        dbconn.close()

def init_app(app):
    app.before_request(_open_db)
    app.teardown_appcontext(_close_db)
