==================================================
Intercom-rank: a service where Intercom meets AWIS
==================================================

This service adds more information about your users using by `AWIS <http://aws.amazon.com/awis/>`_. According to their emails, try to fill next helpful information:

* User's site title, description, online since.
* User's site language.
* User's site rank, rank in default country, page views (per million).


Development
-----------

Service primary built on `Flask <http://flask.pocoo.org>`_.

For local install:

.. code-block:: console

    $ git clone git@github.com:uploadcare/intercom-rank.git
    $ virtualenv venv .
    $ . venv/bin/activate
    $ pip install -r dev.requirements.txt
    $ python manage.py db upgrade

Run service:

.. code-block:: console

    $ python manage.py runserver

Run celery:

.. code-block:: console

    $ celery worker -A app.celery --loglevel debug


Create an admin:

.. code-block:: console

    $ python manage.py create_admin

Run tests:

.. code-block:: console

    $ nose2 tests
