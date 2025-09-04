import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from core.settings import ALLOWED_HOSTS

from .forms import (
    FeedbackForm,
    FeedbackNoForm,
    FeedbackReportForm,
    FeedbackYesForm,
    IssueForm,
)
from .service import send_feedback_notification, send_notifications

log = logging.getLogger(__name__)


def feedback_yes_view(request) -> HttpResponse:
    if request.method == "POST":
        form = FeedbackYesForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            feedback = form.save(commit=False)
            if not request.user.is_anonymous:
                print(request.user)
                feedback.created_by = request.user
            feedback.save()
            success_message = "We'll use it to improve the service."
            context = {"success_message": success_message}
            return render(request, "feedback_success.html", context)
        else:
            return render(request, "yes.html", {"form": form})

    form = FeedbackYesForm()
    url_path = request.GET.get("url_path", "")
    context = {"form": form, "url_path": url_path}
    return render(request, "yes.html", context)


def feedback_no_view(request) -> HttpResponse:
    if request.method == "POST":
        form = FeedbackYesForm(request.POST)
        if form.is_valid():
            success_message = "We'll use it to improve the service."
            context = {"success_message": success_message}
            return render(request, "feedback_success.html", context)
        else:
            return render(request, "no.html", {"form": form})

    form = FeedbackNoForm()
    url_path = request.GET.get("url_path", "")

    context = {"form": form, "url_path": url_path}
    return render(request, "no.html", context)


def feedback_report_view(request) -> HttpResponse:
    if request.method == "POST":

        form = FeedbackYesForm(request.POST)
        if form.is_valid():
            success_message = "We'll use it to improve the service."
            context = {"success_message": success_message}
            return render(request, "feedback_success.html", context)
        else:
            return render(request, "report.html", {"form": form})

    form = FeedbackReportForm()
    url_path = request.GET.get("url_path", "")

    context = {"form": form, "url_path": url_path}
    return render(request, "report.html", context)


def feedback_form_view(request) -> HttpResponse:
    if request.method == "POST":
        form = FeedbackForm(request.POST)
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
            send_notifications(
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
