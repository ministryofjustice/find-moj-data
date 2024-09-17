"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.urls import include, path

app_name = "core"

urlpatterns = [
    path("azure_auth/", include("azure_auth.urls", namespace="azure_auth")),
    path("feedback/", include("feedback.urls", namespace="feedback")),
    path("", include("home.urls", namespace="home")),
    path("", include("django_prometheus.urls")),
]

if settings.DEBUG and not settings.TESTING:
    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()

handler404 = "core.views.handler404"
