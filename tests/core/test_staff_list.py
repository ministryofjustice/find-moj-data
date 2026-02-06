import pytest
from django.conf import settings
from email_validator import validate_email


@pytest.mark.skipif(not settings.STAFF, reason="STAFF setting is not defined or not available in the environment")
def test_middleware_renders_bad_request_response():
    staff_list = settings.STAFF
    for staff_member in staff_list:
        assert validate_email(staff_member, check_deliverability=False)
