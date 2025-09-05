from django.conf import settings
from django.db import models


class FeedbackMixin(models.Model):
    RESEARCH_FEEDBACK_CHOICES = [
        (True, "Yes"),
        (False, "No"),
    ]
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False, null=True
    )

    url_path = models.CharField(max_length=250)
    additional_information = models.TextField(
        verbose_name="Anything else you would like to tell us? (optional)",
        null=True,
        blank=True,
    )
    interested_in_research = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Interested in participating in research to improve the site",
        default=True,
        choices=RESEARCH_FEEDBACK_CHOICES,
    )

    class Meta:
        abstract = True
