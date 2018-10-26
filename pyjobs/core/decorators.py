import requests
from decouple import config
from functools import wraps


def check_recaptcha(function):
    @wraps(function)
    def wrapped(request, *args, **kwargs):
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
    return wrapped 