from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver


class TestSearchWithoutJavascriptAndCss(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_browse_to_first_item(self):
        """
        TODO: incorporate screenshots for debugging
        Convert to pytest
        Tag the test so it doesn't slow down the main CI job
        Factor out steps
        """
        # Navigate to search page
        self.selenium.get(f"{self.live_server_url}")
        self.assertIn("Data catalogue", self.selenium.title)
        search_link = self.selenium.find_element(By.LINK_TEXT, "Search")
        search_link.click()
        self.assertIn("Search", self.selenium.title)

        # Read number of results
        secondary_title = self.selenium.find_element(
            By.CSS_SELECTOR, "h2.govuk-heading-l"
        )
        self.assertRegex(secondary_title.text, r"\d+ Results")

        # Read first result
        first_result = self.selenium.find_element(By.ID, "search-results").find_element(
            By.CSS_SELECTOR, ".govuk-grid-row"
        )
        self.assertTrue(first_result.text)

        # Click the link
        first_link = first_result.find_element(By.CSS_SELECTOR, "h3 a")
        item_name = first_link.text
        first_link.click()

        # Verify we are on the details page
        self.assertIn(item_name, self.selenium.title)
        secondary_title = self.selenium.find_element(
            By.CSS_SELECTOR, "h2.govuk-heading-l"
        )
        self.assertEquals(secondary_title.text, item_name)
