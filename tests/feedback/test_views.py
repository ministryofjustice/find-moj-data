import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestFeedbackView:
    def test_form_renders(self, client):
        response = client.get(reverse("feedback:feedback"), data={})
        assert response.status_code == 200

    def test_invalid_form_renders(self, client):
        response = client.post(reverse("feedback:feedback"), data={})
        assert response.status_code == 200

    def test_valid_form_redirects(self, client):
        response = client.post(
            reverse("feedback:feedback"), data={"satisfaction_rating": 5}
        )
        assert response.status_code == 302
        assert response.url == reverse("feedback:thanks")

    def test_thankyou_renders(self, client):
        response = client.get(reverse("feedback:thanks"), data={})
        assert response.status_code == 200
