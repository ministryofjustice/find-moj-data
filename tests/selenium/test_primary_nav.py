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
        glossary_page,
        chromedriver_path,
        axe_version,
        page_titles,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.home_page = home_page
        self.glossary_page = glossary_page
        self.chromedriver_path = chromedriver_path
        self.page_titles = page_titles
        self.axe_version = axe_version

    def test_glossary_link_from_homepage_works(self):
        self.start_on_the_home_page()
        self.click_on_the_glossary_link()
        self.verify_i_am_on_the_glossary_page()

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        assert self.selenium.title in self.page_titles
        heading_text = self.home_page.primary_heading().text

        assert heading_text == "Find MOJ data"
        assert self.selenium.title.split("-")[0].strip() == "Home"

    def click_on_the_glossary_link(self):
        self.home_page.glossary_nav_link().click()

    def verify_i_am_on_the_glossary_page(self):
        assert self.selenium.title in self.page_titles
        heading_text = self.glossary_page.primary_heading().text

        assert heading_text == self.selenium.title.split("-")[0].strip()
