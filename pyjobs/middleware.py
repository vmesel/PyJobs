import urllib.parse

from django import http
from django.conf import settings
from django.contrib.redirects.middleware import RedirectFallbackMiddleware
from django.contrib.redirects.models import Redirect
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect

from django.middleware.gzip import GZipMiddleware


MAX_AGE = getattr(settings, 'CACHE_CONTROL_MAX_AGE', 2592000)

class RedirectFallbackMiddleware(RedirectFallbackMiddleware):
    response_gone_class = http.HttpResponseGone
    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_response(self, request, response):
        response['Cache-Control'] = 'max-age=%d' % MAX_AGE
        if response.status_code != 404:
            return response

        full_path = request.get_full_path()
        parsed_url = None
        if "?" in full_path:
            parsed_url = urllib.parse.urlparse(full_path)
            full_path = parsed_url.path

        current_site = get_current_site(request)

        r = None
        try:
            r = Redirect.objects.get(site=current_site, old_path=full_path)
        except Redirect.DoesNotExist:
            pass
        if r is None and settings.APPEND_SLASH and not request.path.endswith("/"):
            try:
                if parsed_url is not None:
                    r = Redirect.objects.get(
                        site=current_site,
                        old_path=full_path,
                    )
                else:
                    r = Redirect.objects.get(
                        site=current_site,
                        old_path=request.get_full_path(force_append_slash=True),
                    )
            except Redirect.DoesNotExist:
                pass

        if r is not None:
            if r.new_path == "":
                return self.response_gone_class()

            # Adding back the query parameters to redirecting path
            if parsed_url is not None:
                new_path_with_query_params = r.new_path + "?" + parsed_url.query
                return self.response_redirect_class(new_path_with_query_params)

            # Handles redirections for urls without query parameters
            return self.response_redirect_class(r.new_path)

        return redirect("/")
