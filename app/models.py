from app import db
from flask.ext.login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    awis_access_id = db.Column(db.String(140))
    awis_secret_access_key = db.Column(db.String(140))
    intercom_app_id = db.Column(db.String(140))
    intercom_app_api_key = db.Column(db.String(140))

    def __repr__(self):
        return '<Project #{} {}>'.format(self.id, self.name)
