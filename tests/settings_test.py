from app.settings import *

DEBUG = False
TESTING = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

SERVER_NAME = 'localhost'

WTF_CSRF_ENABLED = False
WTF_CSRF_CHECK_DEFAULT = False
WTF_CSRF_METHODS = []
