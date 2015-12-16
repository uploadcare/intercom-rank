import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'  # todo

# todo switch to PostgreSQL later
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/intercom-rank_dev'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
