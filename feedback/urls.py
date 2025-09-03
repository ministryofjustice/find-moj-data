from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "feedback"

urlpatterns = [
    path(
        "issue",
        views.report_issue_view,
        name="report-issue",
    ),
    path("", views.feedback_form_view, name="feedback"),
    path("yes", views.feedback_yes_view, name="yes"),
    path("no", TemplateView.as_view(template_name="no.html"), name="no"),
    path("report", TemplateView.as_view(template_name="report.html"), name="report"),
    path("thanks", views.thank_you_view, name="thanks"),
]
