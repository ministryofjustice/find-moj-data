import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def reporter():
    user_model = get_user_model()
    return user_model.objects.create(email="reporter@justice.gov.uk")
