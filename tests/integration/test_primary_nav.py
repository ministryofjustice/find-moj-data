import pytest


@pytest.mark.slow
class TestPrimaryNav:
    """
    Given I am on the home page
    Then I should be able to navigate using the primary nav bar
    """

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        home_page,
        chromedriver_path,
        axe_version,
        page_titles,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.home_page = home_page
        self.chromedriver_path = chromedriver_path
        self.page_titles = page_titles
        self.axe_version = axe_version

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        assert self.selenium.title in self.page_titles
        heading_text = self.home_page.primary_heading().text

        assert heading_text == "Find MoJ data"
        assert self.selenium.title.split("-")[0].strip() == "Home"

