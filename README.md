# intercom-rank
small web-service providing intercom + awis integration
with dashboard for initial config

### stack
- Python 3, Flask (Jinja2, WTForms)
- PostgreSQL via SQLAlchemy

### Installation & configuration (development)
- pip install virtualenvwrapper
- git clone git@github.com:uploadcare/intercom-rank.git
- mkvirtualenv --python=/usr/local/bin/python3 intercom-rank
- pip install -r requirements.txt
- ./run.py
- go to localhost:5000/projects

### How to contribute
git-flow, please.

### todo
- use webhook for intercom user creation
- deploy to heroku in order to test webhook
- check if python-awis package is any good for us
- (simple) admin dashboard
- move from sqlite to postgresql before production
- split controllers and models/bl into different packages?
- auth via google account
- docker
- tests