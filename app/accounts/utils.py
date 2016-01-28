from datetime import datetime

from app import app
from app.accounts import User, FreeEmailProvider


def email_is_useful(email, default=False):
    """ Check useful (e.g. non-free) of given email address.
    """
    domain = extract_domain(email)

    if not domain:
        return default

    return not FreeEmailProvider.exists(domain)


def extract_domain(email):
    return (email or '').split('@')[-1].strip()


def create_admin():
    email = app.config['ADMIN_USER']['email']
    password = app.config['ADMIN_USER']['password']

    user = User.query.filter(User.email == email).first()

    if user:
        return user

    user = User(email=email,
                password=app.user_manager.hash_password(password),
                is_enabled=True,
                is_admin=True,
                confirmed_at=datetime.utcnow())
    user.save()
    return user
