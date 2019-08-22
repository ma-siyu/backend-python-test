from functools import wraps
from flask import flash, session, redirect
from .__init__ import *

def login_check(f):
    """
    Checks Google reCAPTCHA.

    :param f: view function
    :return: Function
    """
    @wraps(f)
    def logging(*args, **kwargs):
        if 'logged_in' in session and session['logged_in']:
            return f(*args, **kwargs)
        else:
            flash("Please login first.")
            return redirect('/login')
    return logging
