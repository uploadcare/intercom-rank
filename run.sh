#!/bin/sh
gunicorn manage:app --log-file=-
celery worker -A app.celery --loglevel info
