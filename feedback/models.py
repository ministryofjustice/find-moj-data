from urllib.parse import quote, urlparse, urlunparse

from django.conf import settings
from django.core.validators import MinLengthValidator
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


class Issue(models.Model):
    class IssueChoices(models.TextChoices):
        BROKEN_LINK = "Link is broken"
        INCORRECT_CUSTODIAN = "Data custodian is incorrect"
        OUTDATED_CONTACT = "Contact is outdated"
        OTHER = "Other"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=True
    )

    reason = models.CharField(
        max_length=50,
        choices=IssueChoices.choices,
        verbose_name=_("What is wrong with this page?"),
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
    data_custodian_email = models.CharField(max_length=250)

    @property
    def formatted_entity_url(self):
        parsed_url = urlparse(self.entity_url)
        encoded_path = quote(parsed_url.path)
        formatted_entity_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                encoded_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment,
            )
        )
        return formatted_entity_url
