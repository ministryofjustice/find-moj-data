from django.db import models


class FeedbackMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by_email = models.EmailField(null=True, blank=True)

    url_path = models.CharField(max_length=250)
    additional_information = models.TextField(
        verbose_name="Anything else you would like to tell us? (optional)",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
