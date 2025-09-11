from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path(
        "issue",
        views.report_issue_view,
        name="report-issue",
    ),
    path("yes", views.feedback_view, name="yes"),
    path("no", views.feedback_view, name="no"),
    path("report", views.feedback_view, name="report"),
]
