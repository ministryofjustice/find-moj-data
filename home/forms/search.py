from django.forms import forms


def get_domain_choices():
    """Make API call to obtain domain choices"""
    return [
        ("HMCTS", "HMCTS"),
        ("HMPPS", "HMPPS"),
        ("OPG", "OPG"),
        ("HQ", "HQ"),
    ]


class SearchForm(forms.Form):
    """Django form to represent data product search page inputs"""

    new = forms.BooleanField(default=False)
    query = forms.CharField(max_length=100, strip=False, required=False)
    domains = forms.MultipleChoiceField(
        choices=get_domain_choices, required=False)
    sort = forms.CharField(max_length=15, default="ascending")
    clear_filter = forms.BooleanField(default=False)
    clear_lable = forms.BooleanField(default=False)

    def clean_query(self):
        """Example clean method to apply custom validation to input fields"""
        return str(self.cleaned_data["query"]).capitalize()
