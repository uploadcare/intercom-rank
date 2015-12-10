# intercom-rank
small web-service providing intercom + alexa integration
with dashboard for initial config

### stack
- Python 3, Flask (Jinja2, WTForms)
- PostgreSQL via SQLAlchemy

### Installation & configuration (development)
- git clone
- mkvirtualenv --python=/usr/bin/python3 intercom-rank
- pip install -r requirements.txt
- ./run.py
- go to localhost:5000/projects

### How to contribute
git-flow, please.

### todo
- projects: create action (WTForms)
- simple admin dashboard
- move from sqlite to postgresql before production
- split controllers and models/bl into different packages?
- auth via google account
- tests