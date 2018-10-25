import requests
from decouple import config
from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy

def check_recaptcha(function):
    def wrap(request, *args, **kwargs):
        request.recaptcha_is_valid = None
        if request.method == 'POST':
            recaptcha_response = request.POST.get('g-recaptcha-response')

            if recaptcha_response == '':
                recaptcha_response = None
            else:
                data = {
                    'secret': config('RECAPTCHA_SECRET_KEY'),
                    'response': recaptcha_response
                }

            try:
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            except :
                request.recaptcha_is_valid = False
                return function(request, *args, **kwargs)

            result = r.json()
            if result['success']:
                request.recaptcha_is_valid = True
            else:
                request.recaptcha_is_valid = False
        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap