from datetime import datetime

from flask import abort

from app import db


class PrimaryKeyMixin(object):
    id = db.Column(db.Integer, primary_key=True)


class CreateAndModifyMixin(object):
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow, onupdate=datetime.utcnow)


class BaseModelMixin(PrimaryKeyMixin):
    """ Abstract class for all models in app.
    """
    def save(self):
        """ Shortcut for on operation per session.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_or_404(cls, *args):
        if len(args) == 1 and isinstance(args[0], int):
            args = [cls.id == args[0]]

        item = cls.query.filter(*args).first()

        if item is None:
            raise abort(404)

        return item
