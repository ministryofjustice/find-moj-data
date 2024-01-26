from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("search", views.search_view, name="search"),
    path("search/filter", views.filter_view, name="filter"),
    path("search/clear", views.result_view, name="result_view"),
    path("details", views.details_view, name="details"),
]
