# intercom-rank
small web-service providing intercom + awis integration
with dashboard for initial config

### stack
- Python 3, Flask (Jinja2, WTForms)
- PostgreSQL via SQLAlchemy
- Heroku + gunicorn

### Installation & configuration (development)
- brew install postgresql
- pip install virtualenvwrapper
- git clone git@github.com:uploadcare/intercom-rank.git
- mkvirtualenv --python=/usr/local/bin/python3 intercom-rank
- pip install -r requirements.txt
- createdb -h localhost -p 5432 -U postgres intercom-rank_dev
- heroku local web (better to do this in other console)
- heroku open

### How to contribute
- git-flow, please. http://danielkummer.github.io/git-flow-cheatsheet/

### todo
- use webhook for intercom user creation
- check if python-awis package is any good for us
- (simple) admin dashboard
- split controllers and models/bl into different packages?
- auth via google account
- config (local, dev, prod, ..) management
- move from gunicorn to waitress?..
- move from heroku to digitalocean?..
- docker-compose
- tests