from flask import g

def commit_transaction():
    g.dbconn.commit()

def rollback_transaction():
    g.dbconn.rollback()
