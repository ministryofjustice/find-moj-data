import uuid

from django.core.validators import EmailValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext as _


class Feedback(models.Model):
    SATISFACTION_RATINGS = [
        (5, "Very satisfied"),
        (4, "Satisfied"),
        (3, "Neither satisfied or dissatisfied"),
        (2, "Dissatisfied"),
        (1, "Very dissatisfied"),
    ]

    satisfaction_rating = models.IntegerField(
        choices=SATISFACTION_RATINGS,
        verbose_name=_("Satisfaction survey"),
        null=False,
        blank=False,
    )

    how_can_we_improve = models.TextField(
        verbose_name=_("How can we improve this service?"), null=False, blank=True
    )


class ReportIssue(models.Model):
    class IssueChoices(models.TextChoices):
        BROKEN_LINK = "Broken link"
        INCORRECT_OWNER = "Incorrect owner"
        OUTDATED_CONTACT = "Outdated contact"
        OTHER = "Other"

    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    reason = models.CharField(
        max_length=50,
        choices=IssueChoices.choices,
        verbose_name=_("Reason"),
        null=False,
        blank=False,
    )
    additional_info = models.TextField(
        verbose_name=_("Can you provide more detail?"),
        null=False,
        blank=False,
        validators=[MinLengthValidator(10)],
    )
    entity_name = models.CharField(max_length=250)
    entity_url = models.CharField(max_length=250)
    data_owner_email = models.CharField(max_length=250)
    user_email = models.CharField(
        max_length=250, validators=[EmailValidator()], null=False, blank=True
    )
