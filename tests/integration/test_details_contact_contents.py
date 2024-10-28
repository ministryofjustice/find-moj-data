import pytest
from data_platform_catalogue.entities import (
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
                "https://place-to-get-your-access.com",
                "Select this link for access information (opens in new tab)",
            ),
            (
                "To access these data you need to seek permission from the data owner by email",
                "To access these data you need to seek permission from the data owner by email",
            ),
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
        3 - where no access_requirements custom property exists default to the standrd line
        """
        database.custom_properties.access_information = AccessInformation(
            dc_access_requirements=access_reqs
        )
        mock_get_database_details_response(mock_catalogue, database)

        self.start_on_the_details_page()
        request_access_metadata = self.details_database_page.request_access()

        assert request_access_metadata.text == expected_text

    @pytest.mark.parametrize(
        "access_reqs, slack_channel, owner, expected_text",
        [
            (
                "Some contact info",
                "#contact us",
                "meta.data@justice.gov.uk",
                "Some contact info",
            ),
            (
                "",
                "#contact_us",
                "meta.data@justice.gov.uk",
                "Contact the data owner to request access.",
            ),
            (
                "",
                "",
                "meta.data@justice.gov.uk",
                "Contact the data owner to request access.",
            ),
            (
                "",
                "",
                "",
                "Not provided.",
            ),
        ],
    )
    def test_access_requirements_fallbacks(
        self,
        database,
        mock_catalogue,
        access_reqs,
        slack_channel,
        owner,
        expected_text,
    ):
        if access_reqs:
            database.custom_properties.access_information = AccessInformation(
                dc_access_requirements=access_reqs
            )
        if owner:
            database.governance.data_owner = OwnerRef(
                display_name=owner, email=owner, urn="urn:bla"
            )
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
        "slack_channel, teams_channel, team_email, owner, expected_text",
        [
            (
                "#contact-us",
                "",
                "",
                "meta.data@justice.gov.uk",
                "Slack channel: #contact-us (opens in new tab)",
            ),
            (
                "",
                "Contact us on Teams",
                "",
                "meta.data@justice.gov.uk",
                "Teams channel: Contact us on Teams (opens in new tab)",
            ),
            (
                "",
                "",
                "some-team-email@justice.gov.uk",
                "meta.data@justice.gov.uk",
                "Email: some-team-email@justice.gov.uk",
            ),
            (
                "",
                "",
                "",
                "meta.data@justice.gov.uk",
                "Contact the data owner with questions.",
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
        owner,
        expected_text,
    ):
        if owner:
            database.governance.data_owner = OwnerRef(
                display_name=owner, email=owner, urn="urn:bla"
            )
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
        request_access_metadata = self.details_database_page.contact_channels()

        assert request_access_metadata.text == expected_text

    @pytest.mark.parametrize(
        "owner, expected_text",
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
        owner,
        expected_text,
    ):
        if owner:
            database.governance.data_owner = OwnerRef(
                display_name=owner, email=owner, urn="urn:bla"
            )

        mock_get_database_details_response(mock_catalogue, database)

        self.start_on_the_details_page()
        request_access_metadata = self.details_database_page.data_owner()

        assert request_access_metadata.text == expected_text
