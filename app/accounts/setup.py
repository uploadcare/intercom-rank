from flask_user import UserManager, SQLAlchemyAdapter

from app import db, app
from app.accounts.models import User


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)
user_manager.login_template = 'login.jade'
user_manager.enable_username = False
user_manager.enable_email = True
