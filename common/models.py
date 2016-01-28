from datetime import datetime

from flask import abort
from blinker import signal
from app import db


post_save = signal('post_save')
pre_delete = signal('pre_delete')


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
        post_save.send(self.class_name, instance=self)

    def delete(self):
        pre_delete.send(self.class_name, instance=self)
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

    @property
    def class_name(self):
        cls = type(self)
        return '{}.{}'.format(cls.__module__.split('.')[1], cls.__name__)
