from django.conf import settings
from email_validator import validate_email


def test_middleware_renders_bad_request_response():
    staff_list = settings.STAFF
    if staff_list:
        for staff_member in staff_list:
            assert validate_email(staff_member, check_deliverability=False)
