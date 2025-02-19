import logging

from django.core.validators import MinValueValidator
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import FeedbackForm, IssueForm
from .service import send_feedback_notification, send_notifications

log = logging.getLogger(__name__)


def feedback_form_view(request) -> HttpResponse:
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        form.fields['satisfaction_rating'].validators = [
            MinValueValidator(1, message='Please enter a valid bid')
        ]
        if form.is_valid():
            feedback = form.save()

            user_email = None if request.user.is_anonymous else request.user.email
            verbose_satisfaction_rating = dict(feedback.SATISFACTION_RATINGS).get(
                feedback.satisfaction_rating, feedback.satisfaction_rating
            )
            send_feedback_notification(
                user_email, verbose_satisfaction_rating, feedback.how_can_we_improve
            )

            return redirect("feedback:thanks")
        else:
            log.error(f"Unexpected invalid feedback form submission: {form.errors}")
    else:

        form = FeedbackForm()

    return render(
        request,
        "feedback.html",
        {
            "h1_value": "Give feedback on Find MoJ data",
            "form": form,
        },
    )


def thank_you_view(request) -> HttpResponse:
    return render(
        request,
        "thanks.html",
        {"h1_value": "Thank you for your feedback"},
    )


def report_issue_view(request) -> HttpResponse:
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.entity_name = request.session.get("entity_name")
            issue.entity_url = request.session.get("entity_url")
            issue.data_custodian_email = request.session.get("data_custodian_email")

            # in production, there should always be a signed in user,
            # but this may not be the case in local development/unit tests
            if not request.user.is_anonymous:
                issue.created_by = request.user

            issue.save()

            # Call the send notifications service
            send_notifications(
                issue=issue,
                send_email_to_reporter=form.cleaned_data["send_email_to_reporter"],
            )
            messages.add_message(
                request, messages.SUCCESS, "Thank you for reporting the issue."
            )
            return redirect(request.session.get("entity_url"))

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
            "technical_contact": technical_contact,
        },
    )
