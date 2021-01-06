# Development config, can be used as a base for deployment config but dont reuse the secret values

config = {
    'SECRET_KEY': 'verysecretdevkey',
    'DB_CONN_STR': "user='postgres' dbname='makethempay' host='127.0.0.1' port='5432'",
    'PERMANENT_SESSION_LIFETIME': 600 # 600 seconds = 10 minutes
}
