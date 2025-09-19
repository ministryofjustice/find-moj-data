import pytest

from feedback.forms import (
    FeedbackNoForm,
    FeedbackReportForm,
    FeedbackYesForm,
    IssueForm,
)
from feedback.models import FeedBackNo, FeedBackReport, FeedBackYes, Issue


def test_invalid_feedback_form():
    feedback_forms = [FeedbackNoForm, FeedbackYesForm, FeedbackReportForm]
    for form in feedback_forms:
        assert not form({}).is_valid()


def test_valid_feedback_yes_form():
    form = FeedbackYesForm({"easy_to_find": True, "url_path": "/some-path/"})
    assert form.is_valid()


def test_valid_feedback_no_form():
    form = FeedbackNoForm({"not_clear": True, "url_path": "/some-path/"})
    assert form.is_valid()


def test_valid_feedback_report_form():
    form = FeedbackReportForm({"not_working": True, "url_path": "/some-path/"})
    assert form.is_valid()


@pytest.mark.django_db
def test_feedback_yes_form_saves_to_db():
    form = FeedbackYesForm({"easy_to_find": True, "url_path": "/some-path/"})
    form.save()

    saved = FeedBackYes.objects.first()
    assert saved
    assert saved.easy_to_find is True
    assert saved.url_path == "/some-path/"


@pytest.mark.django_db
def test_feedback_no_form_saves_to_db():
    form = FeedbackNoForm({"not_clear": True, "url_path": "/some-path/"})
    form.save()

    saved = FeedBackNo.objects.first()
    assert saved
    assert saved.not_clear is True
    assert saved.url_path == "/some-path/"


@pytest.mark.django_db
def test_feedback_report_form_saves_to_db():
    form = FeedbackReportForm({"not_working": True, "url_path": "/some-path/"})
    form.save()

    saved = FeedBackReport.objects.first()
    assert saved
    assert saved.not_working is True
    assert saved.url_path == "/some-path/"


def test_valid_report_issue_form():
    assert IssueForm(
        {
            "reason": "Other",
            "additional_info": "a" * 10,
            "send_email_to_reporter": "No",
        }
    ).is_valid()


def test_report_issue_form_invalid_additinal_info_length():
    form = IssueForm({"additional_info": "a" * 9, "send_email_to_reporter": "Yes"})
    assert not form.is_valid()
    assert (
        "Ensure this value has at least 10 characters (it has 9)."
        == form.errors["additional_info"][0]
    )


@pytest.mark.django_db
def test_report_issue_form_saves_to_db(reporter):
    form = IssueForm(
        {
            "additional_info": "a" * 10,
            "send_email_to_reporter": "Yes",
        }
    )

    issue = form.save(commit=False)
    issue.created_by = reporter
    issue.save()

    saved = Issue.objects.first()
    assert saved
    assert saved.additional_info == "a" * 10
    assert saved.created_by == reporter
