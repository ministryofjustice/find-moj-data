import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import FeedbackForm

log = logging.getLogger(__name__)


def feedback_form_view(request) -> HttpResponse:
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("feedback:thanks")
        else:
            log.error(f"Unexpected invalid feedback form submission: {form.errors}")
    else:
        form = FeedbackForm()

    return render(
        request,
        "feedback.html",
        {
            "h1_value": _("Give feedback on Find MOJ data"),
            "form": form,
        },
    )


def thank_you_view(request) -> HttpResponse:
    return render(
        request,
        "thanks.html",
        {"h1_value": _("Thank you for your feedback")},
    )
