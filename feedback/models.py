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
        default=3,
    )

    how_can_we_improve = models.TextField(
        verbose_name=_("How can we improve this service?"), null=False, blank=False
    )
