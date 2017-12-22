from os import environ as os_environ
eget = os_environ.get

settings = {
    'database': eget('DB_DSN', 'mysql+pymysql://puser:puser@mysql/protein_db'),
    'database_async': {
        'host': eget('DB_HOST', 'mysql'),
        'port': int(eget('DB_PORT', 3306)),
        'user': eget('DB_USER', 'puser'),
        'pwd': eget('DB_PASS', 'puser'),
        'db': eget('DB_NAME', 'protein_db'),
        'pool': eget('DB_MAX_POOL', 50),
    },
    'redis': eget('REDIS_DSN', 'redis 6379 0')
}