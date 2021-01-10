import psycopg2

# runs a single query and automatically handles rollbacks on error and commit
# returns error, None or None, returned rows (if any) depending on whether there was an error or not
# helpful for running a single query, but transactions must be handled manually
def run_single_query(conn, query, params):
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
    except psycopg2.Error as e:
        conn.rollback()
        return e, None
    
    returned_rows = cursor.fetchall()

    conn.commit()
    
    return None, returned_rows

