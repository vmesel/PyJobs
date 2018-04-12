from rest_framework import authentication


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'
