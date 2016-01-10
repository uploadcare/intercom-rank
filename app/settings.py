import os

DEBUG = True
# SERVER_NAME = 'localhost:8000'

SECRET_KEY = \
    b'\x84\x92\x7f\xa4\x07\xef`\xb9\xd7\xa0)jA\xe9\xcev1\xdeG\xe3\xfb(]\x80'


DATABASE = {
    'name': 'ranker',
    'host': 'localhost',
    'user': 'postgres',
    'password': '',
}

SQLALCHEMY_TRACK_MODIFICATIONS = True


ADMIN_USER = {
    'email': os.environ.get('RANKER_ADMIN_EMAIL', 'admin@admin.ru'),
    'password': os.environ.get('RANKER_ADMIN_PASSWORD', '123'),
}

CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/9')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/9')
