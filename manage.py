from flask_migrate import MigrateCommand

from app import app, manager


manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    app.run(host='0.0.0.0', port=8000)


if __name__ == "__main__":
    manager.run()
