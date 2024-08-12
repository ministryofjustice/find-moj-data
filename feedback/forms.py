from django.forms import ModelForm
from django.forms.widgets import RadioSelect

from .models import Feedback


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ["satisfaction_rating", "how_can_we_improve"]
        widgets = {
            "satisfaction_rating": RadioSelect(attrs={"class": "govuk-radios__input"})
        }
