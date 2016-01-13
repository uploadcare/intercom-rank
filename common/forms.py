from flask_wtf import Form
from wtforms import StringField


class BaseForm(Form):
    """ Our base class for forms.
    """
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.obj = kwargs.get('obj')


class TrackChangesMixin:
    def __init__(self, *args, **kwargs):
        super(TrackChangesMixin, self).__init__(*args, **kwargs)
        self.is_changed = False

    def populate_obj(self, obj, name):
        old_value = getattr(obj, name)

        super(TrackChangesMixin, self).populate_obj(obj, name)

        new_value = getattr(obj, name)

        self.is_changed = old_value != new_value


class TrackChangesStringField(TrackChangesMixin, StringField):
    pass
