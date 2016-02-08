==================================================
Intercom-rank: a service where Intercom meets AWIS
==================================================

.. image:: /../screenshots/screenshots/index.png
    :alt: Index page
    :width: 100%


This service adds more information about your users using by `AWIS <http://aws.amazon.com/awis/>`_. According to their emails, try to fill next helpful information:

* User's site title, description, online since.
* User's site language.
* User's site rank, rank in default country, page views (per million).

For filtering email addresses domains used a  `free_email_provider_domains.txt <https://gist.github.com/zerc/422e749fa533485122fa>`_ originally created by @tbrianjones.


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


Run tests with output:

.. code-block:: console

    $ nose2 tests -B --log-capture


Screenshosts
------------

Project page. Contains fields for credentials and the control to re-importing existing data.

.. image:: /../screenshots/screenshots/project.png
    :alt: Project's page
    :width: 100%
    

Editable list of providers who grant free email hosting. This list used for filtering users before making an actual request to AWIS.

.. image:: /../screenshots/screenshots/fep.png
    :alt: Editable list of providers of free email hosting
    :width: 100%
