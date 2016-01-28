import logging

from flask import Blueprint


intercom_app = Blueprint('intercom', __name__)
logger = logging.getLogger(__name__)
