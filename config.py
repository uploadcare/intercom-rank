import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'  # todo env

if os.environ.get('DATABSE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/intercom-rank_dev'
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

DEBUG = True
