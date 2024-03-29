from typing import NamedTuple
import os


class Domain(NamedTuple):
    urn: str
    label: str


class DomainModel:
    """
    Store information about domains and subdomains
    """

    def __init__(self):
        self.labels = {}
        # This is temporary whilst we still have the dev enviroment connected to a
        # datahub with different domains.
        if os.environ.get("ENV") == "dev":
            self.top_level_domains = [
                Domain("urn:li:domain:HMCTS", "HMCTS"),
                Domain("urn:li:domain:HMPPS", "HMPPS"),
                Domain("urn:li:domain:HQ", "HQ"),
                Domain("urn:li:domain:LAA", "LAA"),
                Domain("urn:li:domain:OPG", "OPG"),
            ]

            for urn, label in self.top_level_domains:
                self.labels[urn] = label

            self.subdomains = {
                "urn:li:domain:HMPPS": [
                    Domain(
                        "urn:li:domain:2feb789b-44d3-4412-b998-1f26819fabf9", "Prisons"
                    ),
                    Domain(
                        "urn:li:domain:abe153c1-416b-4abb-be7f-6accf2abb10a",
                        "Probation",
                    ),
                ],
                "urn:li:domain:HMCTS": [
                    Domain(
                        "urn:li:domain:4d77af6d-9eca-4c44-b189-5f1addffae55",
                        "Civil courts",
                    ),
                    Domain(
                        "urn:li:domain:31754f66-33df-4a73-b039-532518bc765e",
                        "Crown courts",
                    ),
                    Domain(
                        "urn:li:domain:81adfe94-1284-46a2-9179-945ad2a76c14",
                        "Family courts",
                    ),
                    Domain(
                        "urn:li:domain:b261176c-d8eb-4111-8454-c0a1fa95005f",
                        "Magistrates courts",
                    ),
                ],
                "urn:li:domain:OPG": [
                    Domain(
                        "urn:li:domain:bc091f6c-7674-4c82-a315-f5489398f099",
                        "Lasting power of attourney",
                    ),
                    Domain(
                        "urn:li:domain:efb9ade3-3c5d-4c5c-b451-df9f2d8136f5",
                        "Supervision orders",
                    ),
                ],
                "urn:li:domain:HQ": [
                    Domain(
                        "urn:li:domain:9fb7ff13-6c7e-47ef-bef1-b13b23fd8c7a", "Estates"
                    ),
                    Domain(
                        "urn:li:domain:e4476e66-37a1-40fd-83b9-c908f805d8f4", "Finance"
                    ),
                    Domain(
                        "urn:li:domain:0985731b-8e1c-4b4a-bfc0-38e58d8ba8a1", "People"
                    ),
                    Domain(
                        "urn:li:domain:a320c915-0b43-4277-9769-66615aab4adc",
                        "Performance",
                    ),
                ],
                "urn:li:domain:LAA": [
                    Domain(
                        "urn:li:domain:24344488-d770-437a-ba6f-e6129203b927",
                        "Civil legal advice",
                    ),
                    Domain("urn:li:domain:Legal%20Aid", "Legal aid"),
                    Domain(
                        "urn:li:domain:5c423c06-d328-431f-8634-7a7e86928819",
                        "Public defender",
                    ),
                ],
            }
            for domain, subdomains in self.subdomains.items():
                domain_label = self.labels[domain]
                for urn, subdoman_label in subdomains:
                    self.labels[urn] = f"{domain_label} - {subdoman_label}"
        else:
            self.top_level_domains = [
                Domain("urn:li:domain:courts", "Courts"),
                Domain("urn:li:domain:electronic_monitoring", "Electronic monitoring"),
                Domain("urn:li:domain:general", "General"),
                Domain("urn:li:domain:interventions", "Interventions"),
                Domain("urn:li:domain:opg", "OPG"),
                Domain("urn:li:domain:prison", "Prison"),
                Domain("urn:li:domain:probation", "Probation"),
                Domain("urn:li:domain:risk", "Risk"),
                Domain(
                    "urn:li:domain:victims_case_management", "Victims case management"
                ),
            ]
            self.subdomains = {}

            for urn, label in self.top_level_domains:
                self.labels[urn] = label

    def all_subdomains(self) -> list[Domain]:  # -> list[Any]
        """
        A flat list of all subdomains
        """
        subdomains = []
        for domain_choices in self.subdomains.values():
            subdomains.extend(domain_choices)
        return subdomains

    def get_parent_urn(self, child_subdomain_urn) -> str | None:
        for domain, subdomains in self.subdomains.items():
            for subdomain in subdomains:
                if child_subdomain_urn == subdomain.urn:
                    return domain

    def get_label(self, urn):
        return self.labels.get(urn, urn)
