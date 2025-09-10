import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


@pytest.mark.slow
class TestFeedbackForms:
    """I should be able to access and submit feedback forms on various pages"""

    @pytest.fixture(autouse=True)
    def setup(
        self,
        live_server,
        selenium,
        home_page,
        search_page,
        chromedriver_path,
        axe_version,
        page_titles,
    ):
        self.selenium = selenium
        self.live_server_url = live_server.url
        self.home_page = home_page
        self.search_page = search_page
        self.chromedriver_path = chromedriver_path
        self.page_titles = page_titles
        self.axe_version = axe_version

    def test_succesfull_submission_of_yes_feedback_form_on_home_page(self):
        self.start_on_the_home_page()
        self.click_home_page_feedback_button("feedback-yes-button")
        self.verify_yes_feedback_form_rendered()
        self.populate_yes_feedback_form()
        self.verify_successful_feedback_submission()

    def test_succesfull_submission_of_no_feedback_form_on_home_page(self):
        self.start_on_the_home_page()
        self.click_home_page_feedback_button("feedback-no-button")
        self.verify_no_feedback_form_rendered()
        self.populate_no_feedback_form()
        self.verify_successful_feedback_submission()

    def test_successfull_submission_of_report_problem_form_on_home_page(self):
        self.start_on_the_home_page()
        self.click_home_page_feedback_button("feedback-report-button")
        self.verify_problem_feedback_form_rendered()
        self.populate_problem_feedback_form()
        self.verify_successful_feedback_submission()

    def test_invalid_submission_of_yes_feedback_form_on_home_page(self):
        self.start_on_the_home_page()
        self.click_home_page_feedback_button("feedback-yes-button")
        self.verify_yes_feedback_form_rendered()
        self.populate_yes_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_invalid_submission_of_no_feedback_form_on_home_page(self):
        self.start_on_the_home_page()
        self.click_home_page_feedback_button("feedback-no-button")
        self.verify_no_feedback_form_rendered()
        self.populate_no_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_invalid_submission_of_report_problem_feedback_form_on_home_page(self):
        self.start_on_the_home_page()
        self.click_home_page_feedback_button("feedback-report-button")
        self.verify_problem_feedback_form_rendered()
        self.populate_problem_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_succesfull_submission_of_yes_feedback_form_on_search_page(self):
        self.start_on_the_search_page()
        self.click_search_page_feedback_button("feedback-yes-button")
        self.verify_yes_feedback_form_rendered()
        self.populate_yes_feedback_form()
        self.verify_successful_feedback_submission()

    def test_succesfull_submission_of_no_feedback_form_on_search_page(self):
        self.start_on_the_search_page()
        self.click_search_page_feedback_button("feedback-no-button")
        self.verify_no_feedback_form_rendered()
        self.populate_no_feedback_form()
        self.verify_successful_feedback_submission()

    def test_successfull_submission_of_report_problem_form_on_search_page(self):
        self.start_on_the_search_page()
        self.click_search_page_feedback_button("feedback-report-button")
        self.verify_problem_feedback_form_rendered()
        self.populate_problem_feedback_form()
        self.verify_successful_feedback_submission()

    def test_invalid_submission_of_yes_feedback_form_on_search_page(self):
        self.start_on_the_search_page()
        self.click_search_page_feedback_button("feedback-yes-button")
        self.verify_yes_feedback_form_rendered()
        self.populate_yes_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_invalid_submission_of_no_feedback_form_on_search_page(self):
        self.start_on_the_search_page()
        self.click_search_page_feedback_button("feedback-no-button")
        self.verify_no_feedback_form_rendered()
        self.populate_no_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_invalid_submission_of_report_problem_form_on_search_page(self):
        self.start_on_the_search_page()
        self.click_search_page_feedback_button("feedback-report-button")
        self.verify_problem_feedback_form_rendered()
        self.populate_problem_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_succesfull_submission_of_yes_feedback_form_on_details_page(self):
        self.start_on_the_search_page()
        self.click_on_the_first_result()
        self.verify_i_am_on_the_details_page()
        self.click_details_page_feedback_button("feedback-yes-button")
        self.verify_yes_feedback_form_rendered()
        self.populate_yes_feedback_form()
        self.verify_successful_feedback_submission()

    def test_succesfull_submission_of_no_feedback_form_on_details_page(self):
        self.start_on_the_search_page()
        self.click_on_the_first_result()
        self.verify_i_am_on_the_details_page()
        self.click_details_page_feedback_button("feedback-no-button")
        self.verify_no_feedback_form_rendered()
        self.populate_no_feedback_form()
        self.verify_successful_feedback_submission()

    def test_invalid_submission_of_yes_feedback_form_on_details_page(self):
        self.start_on_the_search_page()
        self.click_on_the_first_result()
        self.verify_i_am_on_the_details_page()
        self.click_search_page_feedback_button("feedback-yes-button")
        self.verify_yes_feedback_form_rendered()
        self.populate_yes_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def test_invalid_submission_of_no_feedback_form_on_details_page(self):
        self.start_on_the_search_page()
        self.click_on_the_first_result()
        self.verify_i_am_on_the_details_page()
        self.click_search_page_feedback_button("feedback-no-button")
        self.verify_no_feedback_form_rendered()
        self.populate_no_feedback_form(invalid=True)
        self.verify_invalid_feedback_submission_shows_errors()

    def verify_i_am_on_the_details_page(self):
        assert "/details/" in self.selenium.current_url

    def click_on_the_first_result(self):
        first_result = self.search_page.first_search_result()
        assert first_result.text
        first_link = first_result.link()
        first_link.click()

    def verify_successful_feedback_submission(self):
        feedback_success_heading = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//h2[text()="Thank you for your feedback"]')
            )
        )
        assert feedback_success_heading is not None

    def verify_invalid_feedback_submission_shows_errors(self):
        error_summary = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "govuk-error-summary__title")
            )
        )
        assert error_summary is not None
        assert error_summary.text == "There is a problem"

    def verify_yes_feedback_form_rendered(self):
        easy_to_find_checkbox = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "id_easy_to_find"))
        )
        assert easy_to_find_checkbox is not None
        assert "Can you tell us more?" in self.selenium.page_source

    def verify_no_feedback_form_rendered(self):
        not_clear = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "id_not_clear"))
        )
        assert not_clear is not None
        assert "Can you tell us more?" in self.selenium.page_source

    def verify_problem_feedback_form_rendered(self):
        not_working = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, "id_not_working"))
        )
        assert not_working is not None
        assert "What is the issue?" in self.selenium.page_source

    def populate_yes_feedback_form(self, invalid=False):
        if not invalid:
            easy_to_find_checkbox = self.selenium.find_element(By.ID, "id_easy_to_find")
            easy_to_find_checkbox.click()

            information_useful = self.selenium.find_element(
                By.ID, "id_information_useful"
            )
            information_useful.click()

            information_easy_to_understand = self.selenium.find_element(
                By.ID, "id_information_easy_to_understand"
            )
            information_easy_to_understand.click()

            addition_information = self.selenium.find_element(
                By.ID, "id_additional_information"
            )
            addition_information.send_keys("This is a test comment")

        submit_button = self.selenium.find_element(By.ID, "submit-feedback-button")
        submit_button.click()

    def populate_no_feedback_form(self, invalid=False):
        if not invalid:
            not_clear = self.selenium.find_element(By.ID, "id_not_clear")
            not_clear.click()

            information_not_avaialable = self.selenium.find_element(
                By.ID, "id_information_not_available"
            )
            information_not_avaialable.click()

            incomplete_information = self.selenium.find_element(
                By.ID, "id_incomplete_information"
            )
            incomplete_information.click()

            difficult_to_understand = self.selenium.find_element(
                By.ID, "id_difficult_to_understand"
            )
            difficult_to_understand.click()

            addition_information = self.selenium.find_element(
                By.ID, "id_additional_information"
            )
            addition_information.send_keys("This is a test comment")

        submit_button = self.selenium.find_element(By.ID, "submit-feedback-button")
        submit_button.click()

    def populate_problem_feedback_form(self, invalid=False):
        if not invalid:
            not_working = self.selenium.find_element(By.ID, "id_not_working")
            not_working.click()

            needs_fixing = self.selenium.find_element(By.ID, "id_needs_fixing")
            needs_fixing.click()

            something_else = self.selenium.find_element(By.ID, "id_something_else")
            something_else.click()

            addition_information = self.selenium.find_element(
                By.ID, "id_additional_information"
            )
            addition_information.send_keys("This is a test comment")

        submit_button = self.selenium.find_element(By.ID, "submit-feedback-button")
        submit_button.click()

    def click_home_page_feedback_button(self, id):
        assert "Was this page useful?" in self.selenium.page_source
        button = self.selenium.find_element(By.ID, id)
        button.click()

    def click_search_page_feedback_button(self, id):
        assert (
            "Did you find what you where looking for today?"
            in self.selenium.page_source
        )
        button = self.selenium.find_element(By.ID, id)
        button.click()

    def click_details_page_feedback_button(self, id):
        assert (
            "Did you find what you where looking for today?"
            in self.selenium.page_source
        )
        button = self.selenium.find_element(By.ID, id)
        button.click()

    def start_on_the_home_page(self):
        self.selenium.get(f"{self.live_server_url}")
        assert self.selenium.title in self.page_titles
        heading_text = self.home_page.primary_heading().text

        assert heading_text == "Discover data from across the Ministry of Justice"
        assert self.selenium.title.split("-")[0].strip() == "Home"

    def start_on_the_search_page(self):
        self.selenium.get(f"{self.live_server_url}/search?new=True")
        assert self.selenium.title in self.page_titles

        heading_text = self.search_page.primary_heading().text
        assert heading_text == "Search MoJ data"
