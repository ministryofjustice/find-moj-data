import csv
import re

from django.core.management.base import BaseCommand

from datahub_client.search.search_types import MultiSelectFilter
from home.service.base import GenericService

RAW_TERMS = [
    "Accumulated Battery Violation",
    "Accumulated Time Violation",
    "Acquisitive Crime",
    "Alcohol Monitoring",
    "Authorised Absence",
    "Breach",
    "Case Manager",
    "Cohort",
    "Community Order",
    "Compliance",
    "Court Bail Order",
    "Curfew",
    "Curfew Absence",
    "Curfew Area",
    "Device Type",
    "Device-Wearer",
    "Dual Tagged",
    "Enforcement Action",
    "Enforcement Officer",
    "Exclusion",
    "Exclusion Geofence",
    "External Agency Request (EAR)",
    "Field Officer",
    "Home Detention Curfew",
    "Immigration and Court Bail",
    "Immigration Enforcement Order",
    "Immigration Removal Centre",
    "Incident",
    "Inclusion Geofence",
    "Inclusion Monitoring",
    "Individual Protocol",
    "Index Disposal",
    "Index Offence",
    "Installation",
    "Installation Attempt",
    "Intensive Monitoring",
    "Licence",
    "Location Monitoring",
    "Multi-Agency Public Protection Arrangements (MAPPA)",
    "Monitoring Equipment",
    "Monitoring Requirements",
    "Multiple Requirement Order",
    "Not Monitored",
    "Notifying Organisation",
    "Order",
    "Order Condition",
    "Order Status",
    "Order Request Type",
    "Police National Computer (PNC)",
    "Post Release Order",
    "Pre-Trial Order",
    "Prolific Priority Offender (PPO)",
    "Protected Characteristics",
    "Radio Frequency Device",
    "Reasonable Excuse",
    "Recall Action",
    "Recordable Offences",
    "Remote Breathalyser Alcohol Monitoring",
    "Responsible Adult",
    "Responsible Officer",
    "Service Request Type",
    "Single Requirement Curfew",
    "Single Requirement Order",
    "Special Immigration Appeals Commission Order",
    "Specials",
    "Suspended Sentence Order",
    "Tamper",
    "Trail Monitoring",
    "Transdermal Alcohol Monitoring",
    "Untagged",
    "Violation Alert",
    "Violation Event",
    "Youth Rehabilitation Order",
]


PARENS = re.compile(r"\([A-Z0-9]+\)")


def normalize(text):
    return PARENS.sub("", text.lower().replace("-", " "))


TERMS = [(term, normalize(term)) for term in RAW_TERMS]


class Command(BaseCommand, GenericService):
    help = """Generate a mapping of URNs to glossary terms, for Electronic Monitoring datasets,
        which can be ingested via Datahub's CSV enricher"""

    def handle(self, *args, **options):
        with open("csv_enricher_input.csv", "w") as csvfile:
            output = csv.writer(csvfile)
            output.writerow(
                (
                    "resource",
                    "subresource",
                    "glossary_terms",
                    "tags",
                    "owners",
                    "ownership_type",
                    "description",
                    "domain",
                    "ownership_type_urn",
                )
            )

            client = self._get_catalogue_client()

            page = 0
            while True:
                results = client.search(
                    filters=[
                        MultiSelectFilter("tags", ["urn:li:tag:Electronic monitoring"])
                    ],
                    page=str(page),
                )
                if not results.page_results:
                    break
                page += 1

                for result in results.page_results:
                    found_terms = []
                    for term, normalized_term in TERMS:
                        if normalized_term in normalize(
                            result.name
                        ) or normalized_term in normalize(result.description):
                            found_terms.append(f"urn:li:glossaryTerm:{term}")

                    if found_terms:
                        output.writerow(
                            (
                                result.urn,
                                "",
                                "|".join(found_terms),
                                "",
                                "",
                                "",
                                "",
                                "",
                                "",
                            )
                        )
