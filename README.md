# intercom-rank
small web-service providing intercom + alexa integration
with dashboard for initial config

### stack
Python 3, Flask, PostgreSQL, SQLAlchemy

### Installation & configuration (development)
- git clone
- mkvirtualenv --python=/usr/bin/python3 intercom-rank
- pip install -r requirements.txt
- ./run.py
- go to localhost:5000/projects

### How to contribute
git-flow, please.

### todo
- projects: list, create actions
- simple admin dashboard
- move from sqlite to postgresql
- tests