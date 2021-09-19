# coding: utf-8
from flask import abort as original_flask_abort
from .response import send
from werkzeug.exceptions import HTTPException


def abort(http_status_code, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    # noinspection PyUnresolvedReferences
    try:
        hint = kwargs.get('message')
        if isinstance(hint, dict):
            msg = ','.join(hint.values())
            original_flask_abort(send(http_status_code, data=hint, msg=msg))
        else:
            original_flask_abort(send(http_status_code, data=hint))
    except HTTPException as e:
        if len(kwargs):
            e.data = kwargs
        raise