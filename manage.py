import os
import sys
import unittest

from flask_migrate import MigrateCommand

from app import app, manager


manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    app.run(host='0.0.0.0', port=8000)


@manager.command
def test():
    TEST_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'tests')

    suite = unittest.loader.TestLoader().discover(TEST_DIR)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        sys.exit('Tests not passed')


if __name__ == "__main__":
    manager.run()
