import pytest

from feedback.forms import FeedbackForm, IssueForm
from feedback.models import Feedback, Issue


def test_invalid_feedback_form():
    assert not FeedbackForm({}).is_valid()


def test_valid_feedback_form():
    assert FeedbackForm({"satisfaction_rating": 5}).is_valid()
    assert FeedbackForm(
        {"satisfaction_rating": 1, "how_can_we_improve": "blah"}
    ).is_valid()


@pytest.mark.django_db
def test_feedback_form_saves_to_db():
    form = FeedbackForm({"satisfaction_rating": 1, "how_can_we_improve": "blah"})
    form.save()

    saved = Feedback.objects.first()
    assert saved
    assert saved.satisfaction_rating == 1
    assert saved.how_can_we_improve == "blah"


def test_valid_report_issue_form():
    assert IssueForm(
        {
            "reason": "Other",
            "additional_info": "a" * 10,
            "send_email_to_reporter": "No",
        }
    ).is_valid()


def test_report_issue_form_invalid_additinal_info_length():
    form = IssueForm(
        {"reason": "Other", "additional_info": "a" * 9, "send_email_to_reporter": "Yes"}
    )
    assert not form.is_valid()
    assert (
        "Ensure this value has at least 10 characters (it has 9)."
        == form.errors["additional_info"][0]
    )


@pytest.mark.django_db
def test_report_issue_form_saves_to_db(reporter):
    form = IssueForm(
        {
            "reason": "Other",
            "additional_info": "a" * 10,
            "send_email_to_reporter": "Yes",
        }
    )

    issue = form.save(commit=False)
    issue.created_by = reporter
    issue.save()

    saved = Issue.objects.first()
    assert saved
    assert saved.reason == "Other"
    assert saved.additional_info == "a" * 10
