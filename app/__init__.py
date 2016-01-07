import os

from flask import Flask
from flask_mail import Mail
from flask_script import Manager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect


template_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'templates')

app = Flask(__name__, template_folder=template_folder)

settings = os.environ.get('RANKER_SETTINGS_FILE', 'settings.py')
app.config.from_pyfile(settings)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
mail = Mail(app)

CsrfProtect(app)


def setup():
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'RANKER_DATABASE_URI',
        'postgres://{user}:{password}@{host}/{name}'.format(
            **app.config['DATABASE'])
        )

    from app import accounts
    app.register_blueprint(accounts.accounts_app)


setup()
