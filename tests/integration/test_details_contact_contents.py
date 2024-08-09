import pytest
from data_platform_catalogue.entities import AccessInformation, CustomEntityProperties

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

    @pytest.mark.parametrize(
        "access_reqs, expected_text, expected_tag",
        [
            (
                "https://place-to-get-your-access.com",
                "Click link for access information (opens in new tab)",
                "a",
            ),
            (
                "To access these data you need to seek permission from the data owner by email",
                "To access these data you need to seek permission from the data owner by email",
                "p",
            ),
            (
                "",
                "Processing the data might require permission from the Data owner.",
                "p",
            ),
        ],
    )
    def test_access_requirements_content(
        self, mock_catalogue, access_reqs, expected_text, expected_tag
    ):
        """
        test that what is displayed in the request action section of contacts is what we expect
        e.g.
        1 - a sole link given is rendered as a hyperlink with standard link text
        2 - some other specific free text held in the access_requirements custom property is
        shown as given
        3 - where no access_requirements custom property exists default to the standrd line
        """
        test_database = generate_database_metadata(
            custom_properties=CustomEntityProperties(
                access_information=AccessInformation(dc_access_requirements=access_reqs)
            )
        )
        mock_get_database_details_response(mock_catalogue, test_database)

        self.start_on_the_details_page()

        request_access_metadata = self.details_database_page.request_access()

        assert request_access_metadata.text == expected_text
        assert request_access_metadata.tag_name == expected_tag

    def start_on_the_details_page(self):
        self.selenium.get(
            f"{self.live_server_url}/details/database/urn:li:container:test"
        )
