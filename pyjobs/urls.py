"""pyjobs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from pyjobs.core.views import handler_404

urlpatterns = [
    url(r"^admin_v2/", admin.site.urls),
    url(r"api/", include("pyjobs.api.urls", namespace="api")),
    url(r"", include("pyjobs.core.urls")),
    url(r"", include("pyjobs.marketing.urls")),
    url(r"", include("pyjobs.partners.urls")),
    url(r"^webpush/", include("webpush.urls")),
    url(
        r"^login/$",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    url(r"^logout/$", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    url(
        r"^password_reset/$",
        auth_views.PasswordResetView.as_view(
            template_name="pythonistas-area-password-change.html"
        ),
        name="password_reset",
    ),
    url("^", include("django.contrib.auth.urls")),
]
handler404 = handler_404
