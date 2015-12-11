# intercom-rank
small web-service providing intercom + alexa integration
with dashboard for initial config

### stack
- Python 3, Flask (Jinja2, WTForms)
- PostgreSQL via SQLAlchemy

### Installation & configuration (development)
- pip install virtualenvwrapper
- git clone git@github.com:uploadcare/intercom-rank.git
- mkvirtualenv --python=/usr/local/bin/python3 intercom-rank
- pip install -r requirements.txt
- mkdir -p env; echo "ACCESS_ID=" > env/awis; echo "SECRET_ACCESS_KEY=" >> env/awis; echo "APP_ID=" > env/intercom; echo "APP_API_KEY=" >> env/intercom
- fill both env files with values
- ./run.py
- go to localhost:5000/projects

### How to contribute
git-flow, please.

### todo
- projects: all required fields (intercom keys, alexa keys)
- simple admin dashboard
- move from sqlite to postgresql before production
- split controllers and models/bl into different packages?
- auth via google account
- docker
- tests