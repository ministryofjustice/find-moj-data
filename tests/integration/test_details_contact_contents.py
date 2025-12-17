import pytest

from datahub_client.entities import (
    AccessInformation,
    Database,
    FurtherInformation,
    OwnerRef,
)
from tests.conftest import (
    generate_database_metadata,
    mock_get_database_details_response,
)


@pytest.mark.slow
class TestDetailsPageContactDetails:
    """
    Given I am in a details page
    When I view the content of the contact information
    Then I should be presented with corrently formated information. A link
    if the request access section is a url, the given free text or if nothing
    given the default text for request access.
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        details_database_page,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.details_database_page = details_database_page

    @pytest.fixture
    def database(self) -> Database:
        result = generate_database_metadata()

        # Blank out owner
        result.governance.data_owner.email = ""
        result.governance.data_owner.display_name = ""

        return result

    def start_on_the_details_page(self):
        self.selenium.get(
            f"{self.live_server_url}/details/database/urn:li:container:test"
        )

    @pytest.mark.parametrize(
        "access_reqs, expected_text",
        [
            (
                "",
                "Learn how to access this data in the Analytical Platform (opens in new tab)",
            ),
            # ( commented out as we're hiding references to data custodians for now
            #     "To access these data you need to seek permission from the data custodian by email",
            #     "To access these data you need to seek permission from the data custodian by email",
            # ),
        ],
    )
    def test_access_requirements_content(
        self, database, mock_catalogue, access_reqs, expected_text
    ):
        """
        test that what is displayed in the request action section of contacts is what we expect
        e.g.
        1 - a sole link given is rendered as a hyperlink with standard link text
        2 - some other specific free text held in the access_requirements custom property is
        shown as given
        3 - where no access_requirements custom property exists default to the standard line
        """
        database.custom_properties.access_information = AccessInformation(
            dc_access_requirements=access_reqs
        )
        database.custom_properties.security_classification = "Official-Sensitive"
        mock_get_database_details_response(mock_catalogue, database)

        self.start_on_the_details_page()
        request_access_metadata = self.details_database_page.request_access()
        print(f"{request_access_metadata.text=}")
        print(f"{expected_text=}")
        assert request_access_metadata.text == expected_text

    @pytest.mark.parametrize(
        "access_reqs, slack_channel, custodian, expected_text",
        [
            # (
            #     "Some contact info",
            #     "#contact us",
            #     "meta.data@justice.gov.uk",
            #     "Some contact info",
            # ),
            # (
            #     "",
            #     "#contact_us",
            #     "meta.data@justice.gov.uk",
            #     "Contact the data custodian to request access.",
            # ),
            # (
            #     "",
            #     "",
            #     "meta.data@justice.gov.uk",
            #     "Contact the data custodian to request access.",
            # ),
            (
                "",
                "",
                "",
                "Learn how to access this data in the Analytical Platform (opens in new tab)",
            ),
        ],
    )
    def test_access_requirements_fallbacks(
        self,
        database,
        mock_catalogue,
        access_reqs,
        slack_channel,
        custodian,
        expected_text,
    ):
        database.custom_properties.security_classification = "Official-Sensitive"
        if access_reqs:
            database.custom_properties.access_information = AccessInformation(
                dc_access_requirements=access_reqs
            )
        if custodian:
            database.governance.data_custodians = [
                OwnerRef(display_name=custodian, email=custodian, urn="urn:bla")
            ]
        else:
            database.governance.data_custodians = []

        if slack_channel:
            database.custom_properties.further_information = FurtherInformation(
                dc_slack_channel_name=slack_channel,
                dc_slack_channel_url="http://bla.com",
            )

        mock_get_database_details_response(mock_catalogue, database)

        self.start_on_the_details_page()
        request_access_metadata = self.details_database_page.request_access()

        assert request_access_metadata.text == expected_text

    @pytest.mark.parametrize(
        "slack_channel, teams_channel, team_email, custodian, expected_text",
        [
            (
                "#contact-us",
                "",
                "",
                "meta.data@justice.gov.uk",
                "Slack (opens in new tab)",
            ),
            (
                "",
                "Contact us on Teams",
                "",
                "meta.data@justice.gov.uk",
                "MS Teams (opens in new tab)",
            ),
            (
                "",
                "",
                "some-team-email@justice.gov.uk",
                "meta.data@justice.gov.uk",
                "some-team-email@justice.gov.uk",
            ),
            (
                "",
                "",
                "",
                "meta.data@justice.gov.uk",
                "Contact the data custodian with questions.",
            ),
            (
                "",
                "",
                "",
                "",
                "Not provided.",
            ),
        ],
    )
    def test_contact_channels_fallbacks(
        self,
        database,
        mock_catalogue,
        slack_channel,
        teams_channel,
        team_email,
        custodian,
        expected_text,
    ):
        if custodian:
            database.governance.data_custodians = [
                OwnerRef(display_name=custodian, email=custodian, urn="urn:bla")
            ]
        else:
            database.governance.data_custodians = []

        if slack_channel:
            database.custom_properties.further_information = FurtherInformation(
                dc_slack_channel_name=slack_channel,
                dc_slack_channel_url="http://bla.com",
            )
        if teams_channel:
            database.custom_properties.further_information = FurtherInformation(
                dc_teams_channel_name=teams_channel,
                dc_teams_channel_url="http://bla.com",
            )
        if team_email:
            database.custom_properties.further_information = FurtherInformation(
                dc_team_email=team_email,
            )

        mock_get_database_details_response(mock_catalogue, database)

        self.start_on_the_details_page()

        if slack_channel:
            assert self.details_database_page.contact_channels_slack()
        if teams_channel:
            assert self.details_database_page.contact_channels_ms_teams()
        if team_email:
            assert self.details_database_page.contact_channels_team_email()

        # if not slack_channel and not teams_channel and not team_email and custodian:
        #     assert self.details_database_page.contact_channels_data_owner()
        if not slack_channel and not teams_channel and not team_email and not custodian:
            assert self.details_database_page.contact_channels_not_provided()

    @pytest.mark.parametrize(
        "custodian, expected_text",
        [
            (
                "meta.data@justice.gov.uk",
                "meta.data@justice.gov.uk",
            ),
            (
                "",
                "Not provided - contact the Data Catalogue team about this data.",
            ),
        ],
    )
    def test_data_owner_fallbacks(
        self,
        database,
        mock_catalogue,
        custodian,
        expected_text,
    ):
        if custodian:
            database.governance.data_custodians = [
                OwnerRef(display_name=custodian, email=custodian, urn="urn:bla")
            ]
        else:
            database.governance.data_custodians = []

        mock_get_database_details_response(mock_catalogue, database)

        self.start_on_the_details_page()
        # request_access_metadata = self.details_database_page.data_owner_or_custodian()

        # assert request_access_metadata.text == expected_text
