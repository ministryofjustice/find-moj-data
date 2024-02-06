from django import forms


def get_domain_choices():
    """Make API call to obtain domain choices"""
    # TODO: pull in the domains from the catalogue client
    # facets = client.search_facets()
    # domain_list = facets.options("domains")
    return [
        ("HMCTS", "HMCTS"),
        ("HMPPS", "HMPPS"),
        ("OPG", "OPG"),
        ("HQ", "HQ"),
    ]


def get_sort_choices():
    return [
        ("relevance", "Relevance"),
        ("ascending", "Ascending"),
        ("descending", "Descending"),
    ]


class SearchForm(forms.Form):
    """Django form to represent data product search page inputs"""

    new = forms.BooleanField(initial=False)
    query = forms.CharField(max_length=100, strip=False, required=False)
    domains = forms.MultipleChoiceField(choices=get_domain_choices, required=False)
    sort = forms.ChoiceField(
        choices=get_sort_choices,
        widget=forms.RadioSelect(
            attrs={"class": "govuk-radios__input", "form": "searchform"}
        ),
        initial="relevance",
    )
    clear_filter = forms.BooleanField(initial=False)
    clear_label = forms.BooleanField(initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["sort"] = "relevance"

    def clean_query(self):
        """Example clean method to apply custom validation to input fields"""
        return str(self.cleaned_data["query"]).capitalize()
