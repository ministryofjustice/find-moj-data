import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from core.settings import ALLOWED_HOSTS

from .forms import (
    FeedbackNoForm,
    FeedbackReportForm,
    FeedbackYesForm,
    IssueForm,
)
from .service import (
    send_feedback_notification,
    send_issue_notifications,
)

log = logging.getLogger(__name__)


def feedback_view(request) -> HttpResponse:
    url_path = request.GET.get("url_path", "")
    field_set = []

    if request.method == "POST":
        success_message = "We'll use it to improve the service."

        match request.path:
            case "/feedback/yes":
                form = FeedbackYesForm(request.POST)
                subject = "Is this page useful - Yes"
            case "/feedback/no":
                form = FeedbackNoForm(request.POST)
                subject = "Is this page useful - No"
            case _:
                form = FeedbackReportForm(request.POST)
                success_message = "We look at every report received."
                subject = "Report an issue with this page"

        if form.is_valid():
            feedback = form.save(commit=False)
            # In production, there should always be a signed in user,
            # but this may not be the case in local development/unit tests
            if not request.user.is_anonymous:
                feedback.created_by_email = request.user.email

            feedback.save()

            # Send notification
            send_feedback_notification(feedback, subject)

            context = {"success_message": success_message}
            return render(request, "feedback_success.html", context)
        else:

            for field in form:
                if field.widget_type == "checkbox":
                    field_set.append(field)
            log.info(f"invalid feedback form submission: {form.errors}")
            return render(
                request,
                "feedback_form.html",
                {
                    "form": form,
                    "url_path": url_path,
                    "field_set": field_set,
                },
            )

    legend_label = "Can you tell us more?"
    match request.path:
        case "/feedback/yes":
            form = FeedbackYesForm()
        case "/feedback/no":
            form = FeedbackNoForm()
        case _:
            form = FeedbackReportForm()
            legend_label = "What is the issue?"
    for field in form:
        if field.widget_type == "checkbox":
            field_set.append(field)

    context = {
        "form": form,
        "field_set": field_set,
        "url_path": url_path,
        "legend_label": legend_label,
    }
    return render(request, "feedback_form.html", context)


def report_issue_view(request) -> HttpResponse:
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.entity_name = request.session.get("entity_name")
            issue.entity_url = request.session.get("entity_url")
            issue.data_custodian_email = request.session.get("data_custodian_email")

            is_valid_url = url_has_allowed_host_and_scheme(
                url=issue.entity_url,
                allowed_hosts=ALLOWED_HOSTS,
                require_https=False,
            )
            if not is_valid_url:
                log.error(f"Invalid entity URL: {issue.entity_url}")
                return HttpResponse(status=400)

            # in production, there should always be a signed in user,
            # but this may not be the case in local development/unit tests
            if not request.user.is_anonymous:
                issue.created_by = request.user

            issue.save()

            # Call the send notifications service
            send_issue_notifications(
                issue=issue,
                send_email_to_reporter=form.cleaned_data["send_email_to_reporter"],
            )
            messages.add_message(
                request, messages.SUCCESS, "Feedback submitted successfully"
            )
            if is_valid_url:
                return redirect(issue.entity_url)
            else:
                return redirect("/")

        else:
            log.info(f"Invalid report issue form submission: {form.errors}")
            entity_url = request.session["entity_url"]
            return render(
                request,
                "report_issue.html",
                {
                    "h1_value": "Report an issue with %s"
                    % (request.session.get("entity_name")),
                    "form": form,
                    "entity_url": entity_url,
                    "report": True,

                },
            )
    else:
        entity_name = request.GET.get("entity_name")
        entity_url = request.GET.get("entity_url")

        request.session["entity_name"] = entity_name
        request.session["entity_url"] = entity_url
        request.session["data_custodian_email"] = request.GET.get(
            "data_custodian_email", ""
        )

        form = IssueForm()

    technical_contact = True if request.session.get("data_custodian_email") else False
    return render(
        request,
        "report_issue.html",
        {
            "h1_value": f"Report an issue with {entity_name}",
            "form": form,
            "entity_name": entity_name,
            "entity_url": entity_url,
            "report": True,
            "technical_contact": technical_contact,
        },
    )
