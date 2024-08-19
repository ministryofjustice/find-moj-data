import pytest

from feedback.forms import FeedbackForm
from feedback.models import Feedback


def test_invalid_form():
    assert not FeedbackForm({}).is_valid()


def test_valid_form():
    assert FeedbackForm({"satisfaction_rating": 5}).is_valid()
    assert FeedbackForm(
        {"satisfaction_rating": 1, "how_can_we_improve": "blah"}
    ).is_valid()


@pytest.mark.django_db
def test_form_saves_to_db():
    form = FeedbackForm({"satisfaction_rating": 1, "how_can_we_improve": "blah"})
    form.save()

    saved = Feedback.objects.first()
    assert saved
    assert saved.satisfaction_rating == 1
    assert saved.how_can_we_improve == "blah"
