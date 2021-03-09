from django.conf.urls import include, url
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse

from pyjobs.blog.views import *

urlpatterns = [
    url(r"^$", blog_index, name="blog_index"),
    url(r"^(?P<unique_slug>[-\w\d]+)$", blog_post, name="blog_post"),
    url(r"^tag/(?P<unique_slug>[-\w\d]+)$", blog_tag_view, name="blog_tag"),
]
