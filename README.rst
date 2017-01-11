==================================================
Intercom-rank: domain ranking for Intercom
==================================================

About
-----------
Intercom Rank adds the actual domain rank, language and a site description from Alexa for any lead or customer in your Intercom dashboard.

.. image:: /../screenshots/screenshots/intercom-rank-1.gif
    :alt: List of customers


You can use the domain rank and language to set up different drip campaigns and assign leads to the most awesome sales people in your team.

.. image:: /../screenshots/screenshots/intercom-rank-3.png
    :alt: Assign to Sales team


Intercom Rank adds more information about your leads and customers from AWIS. According to their email domains, it tries to fill some helpful information:

* User's site title, description, online since.
* User's site language.
* User's site rank, country ranking, page views (per million).

Disclaimer
-----------
`Intercom <https://www.intercom.io/customer-engagement>`_ is a powerful marketing automation platform that allows you to communicate with your leads and customers.

`Alexa <http://alexa.com>`_ is a web analytics toolkit that provides tons of useful information about any website, including the domain rank and estimated monthly traffic. There is an API to get the data, it called `AWIS <http://docs.aws.amazon.com/AlexaWebInfoService/latest/>`_.

Intercom Rank was developed by `Uploadcare <https://uploadcare.com>`_  team.


Requirements
------------

* Python 3+.
* `Redis <http://redis.io>`_.
* `AWIS <http://aws.amazon.com/awis/>`_ account.
* `Intercom <https://www.intercom.io>`_ account.


Quick start
-----------

The service was primarily built on `Flask <http://flask.pocoo.org>`_.

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


Settings
------------

The list of projects.

.. image:: /../screenshots/screenshots/index.png
    :alt: Index page
    :width: 100%


Project page. It contains fields for credentials and the control for re-importing existing data.

.. image:: /../screenshots/screenshots/project.png
    :alt: Project's page
    :width: 100%


Editable list of providers who grant free email hosting. This list used for filtering users before making an actual request to AWIS.

.. image:: /../screenshots/screenshots/fep.png
    :alt: Editable list of providers of free email hosting
    :width: 100%


We used `free_email_provider_domains.txt <https://gist.github.com/tbrianjones/5992856>`_ originally created by `@tbrianjones <https://gist.github.com/tbrianjones>`_ to automatically remove free email services.

Contributors
------------

- `@zerc`_
- `@dmitry-mukhin`_
- `@igordebatur`_

.. _@zerc: https://github.com/zerc
.. _@dmitry-mukhin: https://github.com/dmitry-mukhin
.. _@igordebatur: https://github.com/igordebatur

License
------------
This codebase is licensed under the GNU GPL v3.0 License license.

Want to help?
------------
Want to file a bug, contribute some code, or improve documentation? Awesome!

If you think you ran into something in Uploadcare libraries which might
have security implications, please hit us up at `bugbounty@uploadcare.com`_ or Hackerone.

We'll contact you personally in a short time to fix an issue through
co-op and prior to any public disclosure.

.. _bugbounty@uploadcare.com: mailto:bugbounty@uploadcare.com
