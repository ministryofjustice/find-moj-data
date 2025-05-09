from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("search", views.search_view, name="search"),
    path("glossary", views.glossary_view, name="glossary"),
    path("glossary/<str:urn>", views.glossary_term_view, name="glossary_term"),
    path(
        "glossary/<str:urn>/pagination/<str:page>",
        views.glossary_term_view,
        name="glossary_term_pagination",
    ),
    path(
        "metadata_specification",
        views.metadata_specification_view,
        name="metadata_specification",
    ),
    path(
        "details/<str:result_type>/<str:urn>.csv",
        views.details_view_csv,
        name="details_csv",
    ),
    path(
        "details/<str:result_type>/<str:urn>",
        views.details_view,
        name="details",
    ),
    path("pagination/<str:page>", views.search_view, name="pagination"),
    path("cookies", views.cookies_view, name="cookies"),
    path(
        "accessibility_statement",
        views.accessibility_statement_view,
        name="accessibility_statement",
    ),
]
