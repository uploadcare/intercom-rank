import os

ENVIRON = os.environ.get('ENVIRON', 'LOCAL')

DEBUG = ENVIRON == 'LOCAL'

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    b'\x84\x92\x7f\xa4\x07\xef`\xb9\xd7\xa0)jA\xe9\xcev1\xdeG\xe3\xfb(]\x80'
)


DATABASE = {
    'name': os.environ.get('DB_NAME', 'ranker'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', ''),
}

SQLALCHEMY_TRACK_MODIFICATIONS = DEBUG


ADMIN_USER = {
    'email': os.environ.get('RANKER_ADMIN_EMAIL', 'admin@admin.ru'),
    'password': os.environ.get('RANKER_ADMIN_PASSWORD', '123'),
}

# Rename to 'CELERY_REDIS_URL'
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/9')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/9')

REDIS_CONF = os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/9')

AWIS_USER_LIMIT_FOR_PROJECT = int(os.environ.get('LIMIT_FOR_PROJECT', 30))
