from datetime import datetime

from app import app, manager, db
from app.accounts import User


@manager.command
def create_admin():
    email = app.config['ADMIN_USER']['email']
    password = app.config['ADMIN_USER']['password']

    user = User.query.filter(User.email == email).first()

    if user:
        return

    user = User(email=email,
                password=app.user_manager.hash_password(password),
                is_enabled=True,
                is_admin=True,
                confirmed_at=datetime.utcnow())
    user.save()
