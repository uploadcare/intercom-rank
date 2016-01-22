from app.accounts.utils import create_admin as _create_admin


from app import manager


@manager.command
def create_admin():
    _create_admin()
