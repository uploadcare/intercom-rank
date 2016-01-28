import os

import redis
from flask import Flask
from flask_mail import Mail
from flask_script import Manager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from celery import Celery


PROJECT_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..')

TEMPLATES_FOLDER = os.path.join(PROJECT_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_FOLDER)

settings = os.environ.get('RANKER_SETTINGS_FILE', 'settings.py')
app.config.from_pyfile(settings)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
mail = Mail(app)

redis_pool = redis.ConnectionPool.from_url(app.config['REDIS_CONF'])

csrf = CsrfProtect(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


def setup():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgres://{user}:{password}@{host}/{name}'.format(
            **app.config['DATABASE'])
        )

    from app import accounts
    from app import intercom
    app.register_blueprint(accounts.accounts_app)
    app.register_blueprint(intercom.intercom_app)


setup()
