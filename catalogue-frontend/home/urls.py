from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("search", views.search_view, name="search"),
    path("glossary", views.glossary_view, name="glossary"),
    path(
        "details/<str:result_type>/<str:id>",
        views.details_view,
        name="details",
    ),
    path("pagination/<str:page>", views.search_view, name="pagination"),
]
