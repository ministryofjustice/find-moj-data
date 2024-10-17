import logging
import threading

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import FeedbackForm, ReportIssueForm
from .service.notify import send_notifications

log = logging.getLogger(__name__)

mitch = "mitch.dawson@digital.justice.gov.uk"


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


def report_issue_view(request) -> HttpResponse:
    if request.method == "POST":
        form = ReportIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.entity_name = request.session.get("entity_name")
            issue.entity_url = request.session.get("entity_url")
            issue.data_owner_email = request.session.get("data_owner_email")
            issue.data_owner_email = mitch
            issue.save()

            # Create a seperate thread to run the sending of notifcations, to avoid
            t = threading.Thread(target=send_notifications, args=(issue,))
            t.start()

            return redirect("feedback:thanks")

        else:
            log.error(f"Unexpected invalid report issue form submission: {form.errors}")
            return render(
                request,
                "report_issue.html",
                {
                    "h1_value": _("Report an issue on Find MOJ data"),
                    "form": form,
                },
            )
    else:
        entity_name = _(request.GET.get("entity_name"))
        entity_url = _(request.GET.get("entity_url"))

        request.session["entity_name"] = entity_name
        request.session["entity_url"] = entity_url
        request.session["entity_path"] = _(request.GET.get("entity_path"))
        request.session["data_owner_email"] = _(request.GET.get("data_owner_email", ""))

        form = ReportIssueForm()

    return render(
        request,
        "report_issue.html",
        {
            "h1_value": _("Report an issue on Find MOJ data"),
            "form": form,
            "entity_name": entity_name,
            "entity_url": entity_url,
        },
    )
