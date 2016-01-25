from datetime import datetime

from app import app
from app.accounts import User, FreeEmailProvider


def transform_email_if_useful(email, user_id):
    """ Helper which transform original email to: user_id@email_domain.com
    If it is useful (e.g. non-free).
    """
    email_domain = (email or '').split('@')[-1].strip()

    if not email_domain or FreeEmailProvider.exists(email_domain):
        return None

    return '{}@{}'.format(user_id, email_domain)


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
