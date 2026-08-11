import logging
from urllib.parse import urlparse

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

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


def _build_report_issue_back_link_context(entity_url: str | None, entity_type: str | None) -> dict[str, str]:
    fallback_url = entity_url or reverse("home:home")
    fallback_label = (entity_type or "home").strip().lower()
    return {
        "back_fallback_url": fallback_url,
        "back_fallback_label": fallback_label,
    }


def feedback_view(request) -> HttpResponse:
    url_path = request.GET.get("url_path", "")
    field_set = []

    if request.path == "/feedback/yes":
        feedback_type = "yes"
    elif request.path == "/feedback/no":
        feedback_type = "no"
    else:
        feedback_type = "report"

    if request.method == "POST":
        success_message = "We'll use it to improve the service."
        legend_label = "Can you tell us more?"

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
                legend_label = "What is the issue?"
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

            return render(
                request,
                "feedback_success.html",
                {
                    "success_message": success_message,
                    "feedback_type": feedback_type,
                },
            )

        else:
            for field in form:
                if field.widget_type == "checkbox":
                    field_set.append(field)
            if hasattr(form, "get_error_summary_items"):
                summary_errors = form.get_error_summary_items()
            else:
                summary_errors = [
                    {
                        "href": ("feedback-errors" if errored_field == "__all__" else f"id_{errored_field}"),
                        "message": error,
                    }
                    for errored_field, error_messages in form.errors.items()
                    for error in error_messages
                ]
            log.info(f"invalid feedback form submission: {form.errors}")

            return render(
                request,
                "feedback_form.html",
                {
                    "form": form,
                    "summary_errors": summary_errors,
                    "url_path": url_path,
                    "field_set": field_set,
                    "legend_label": legend_label,
                    "feedback_type": feedback_type,
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
        "summary_errors": [],
        "field_set": field_set,
        "url_path": url_path,
        "legend_label": legend_label,
        "feedback_type": feedback_type,
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

            if issue.entity_url:
                parsed_url = urlparse(issue.entity_url)
                is_valid_url = parsed_url.scheme in ["http", "https"] and (
                    not parsed_url.hostname or parsed_url.hostname in ALLOWED_HOSTS
                )
            else:
                is_valid_url = True

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
                request,
                messages.SUCCESS,
                "Thank you for reporting an issue. We look at every report received.",
            )
            if is_valid_url:
                return redirect(issue.entity_url)
            else:
                return redirect("/")

        else:
            log.info(f"Invalid report issue form submission: {form.errors}")

            entity_url = request.session.get("entity_url")
            entity_type = request.session.get("entity_type")
            back_link_context = _build_report_issue_back_link_context(entity_url, entity_type)

            return render(
                request,
                "report_issue.html",
                {
                    "h1_value": "Report an issue",
                    "form": form,
                    "entity_name": request.session.get("entity_name"),
                    "entity_type": request.session.get("entity_type"),
                    "entity_url": request.session.get("entity_url"),
                    "entity_system_name": request.session.get("entity_system_name"),
                    "subject_area": request.session.get("subject_area"),
                    "parent_entity": request.session.get("parent_entity"),
                    "parent_entity_url": request.session.get("parent_entity_url"),
                    "parent_entity_type": request.session.get("parent_entity_type"),
                    "parent_entity_friendly_name": request.session.get("parent_entity_friendly_name"),
                    "report": True,
                    **back_link_context,
                },
            )
    else:
        # GET handler
        entity_url = request.GET.get("entity_url")
        parsed_url = None

        if entity_url:
            parsed_url = urlparse(entity_url)

            if parsed_url.scheme not in ["http", "https"]:
                log.warning(f"Invalid url scheme: {parsed_url.scheme} in entity_url: {entity_url}")
                return HttpResponse(status=400)

        hostname = parsed_url.hostname if parsed_url else None
        if hostname and hostname not in ALLOWED_HOSTS:
            log.warning(
                "Invalid hostname in entity_url: %s. Allowed hosts: %s",
                hostname,
                ALLOWED_HOSTS,
            )
            return HttpResponse(status=400)

        entity_name = (request.GET.get("entity_name") or "").strip() or None
        entity_type = (request.GET.get("entity_type") or "").strip() or None
        entity_system_name = (request.GET.get("entity_system_name") or "").strip() or None
        subject_area = (request.GET.get("subject_area") or "").strip() or None
        parent_entity = (request.GET.get("parent_entity") or "").strip() or None
        parent_entity_url = (request.GET.get("parent_entity_url") or "").strip() or None
        parent_entity_type = (request.GET.get("parent_entity_type") or "").strip() or None
        parent_entity_friendly_name = (request.GET.get("parent_entity_friendly_name") or "").strip() or None

        request.session["entity_name"] = entity_name
        request.session["entity_type"] = entity_type
        request.session["entity_url"] = entity_url
        request.session["entity_system_name"] = entity_system_name
        request.session["subject_area"] = subject_area
        request.session["parent_entity"] = parent_entity
        request.session["parent_entity_url"] = parent_entity_url
        request.session["parent_entity_type"] = parent_entity_type
        request.session["parent_entity_friendly_name"] = parent_entity_friendly_name

        request.session["data_custodian_email"] = request.GET.get("data_custodian_email", "")

        form = IssueForm()

    back_link_context = _build_report_issue_back_link_context(entity_url, entity_type)
    technical_contact = True if request.session.get("data_custodian_email") else False
    return render(
        request,
        "report_issue.html",
        {
            "h1_value": "Report an issue",
            "form": form,
            "entity_name": entity_name,
            "entity_type": entity_type,
            "entity_url": entity_url,
            "entity_system_name": entity_system_name,
            "subject_area": subject_area,
            "report": True,
            "technical_contact": technical_contact,
            "parent_entity": parent_entity,
            "parent_entity_url": parent_entity_url,
            "parent_entity_type": parent_entity_type,
            "parent_entity_friendly_name": parent_entity_friendly_name,
            **back_link_context,
        },
    )
