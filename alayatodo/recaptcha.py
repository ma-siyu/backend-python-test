"""
A script for checking if google reCAPTCHA is valid to protect app from spam and abuse.
This was adapted from a post from Jonathan Rusk on 2018/03/08 to Chromis.
The url here:
https://www.chromis.com/flask_recaptcha/
"""

import requests
from functools import wraps
from flask import flash, request
from .__init__ import *

def recaptcha(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.recaptcha_is_valid = None

        if request.method == 'POST':
            data = {
                'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': request.form.get('g-recaptcha-response'),
                'remoteip': request.access_route[0]
            }

            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data=data
            )
            result = r.json()

            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
                flash('Invalid reCAPTCHA. Please try again.', 'error')

        return f(*args, **kwargs)

    return decorated_function
