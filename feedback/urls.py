from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.feedback_form_view, name="feedback"),
    path("thanks", views.thank_you_view, name="thanks"),
]
