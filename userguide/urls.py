from django.urls import path

from .views import userguide_view

app_name = "userguide"

urlpatterns = [
    path("userguide/<slug:slug>/", userguide_view, name="userguide_detail"),
    path("userguide/", userguide_view, name="userguide_index"),
]
