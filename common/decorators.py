from functools import wraps

from flask import render_template
from werkzeug.wrappers import BaseResponse

__ALL__ = ('render_to',)


def render_to(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            status_code = 200
            ctx = f(*args, **kwargs) or {}

            if isinstance(ctx, BaseResponse):
                return ctx

            if isinstance(ctx, tuple):
                ctx, status_code = ctx

            template_name = template
            if template_name is None:
                template_name = f.__name__ + '.jade'

            return render_template(template_name, **ctx), status_code
        return decorated_function
    return decorator
