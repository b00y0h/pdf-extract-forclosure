# court_scraper_headless.py
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime
import io
import time

class CourtScraperHeadless:
    def __init__(self, streamlit_instance):
        self.base_url = "https://www.courtclerk.org"
        self.st = streamlit_instance
        self.driver = None

    def initialize_browser(self):
        """Initialize the Chrome browser in headless mode"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920x1080")
            
            # Initialize undetected-chromedriver
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path='/usr/bin/chromedriver',
                browser_executable_path='/usr/bin/google-chrome'
            )
            return True
        except Exception as e:
            self.st.error(f"Error initializing browser: {str(e)}")
            return False

    def cleanup(self):
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def search_foreclosures(self, begin_date, end_date=None):
        """Search foreclosures between dates"""
        try:
            if not self.initialize_browser():
                return None

            if not end_date:
                end_date = datetime.now().strftime("%m/%d/%Y")

            # Navigate to the foreclosure search page
            self.st.write("Navigating to foreclosure search page...")
            self.driver.get(f"{self.base_url}/records-search/foreclosure/")

            # Wait for and select 'All of the above' option
            self.st.write("Selecting search criteria...")
            wait = WebDriverWait(self.driver, 10)
            select_element = wait.until(
                EC.presence_of_element_located((By.NAME, "ccode"))
            )
            Select(select_element).select_by_value("A")

            # Fill in the dates
            begin_date_input = wait.until(
                EC.presence_of_element_located((By.NAME, "begdate"))
            )
            begin_date_input.clear()
            begin_date_input.send_keys(begin_date)

            end_date_input = self.driver.find_element(By.NAME, "enddate")
            end_date_input.clear()
            end_date_input.send_keys(end_date)

            # Click search button and wait for results
            self.st.write("Submitting search...")
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            submit_button.click()

            # Wait for results table
            wait.until(
                EC.presence_of_element_located((By.ID, "cpciv_classification_results"))
            )

            # Find first row's document link and click it
            self.st.write("Finding first result...")
            first_row = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#cpciv_classification_results tbody tr"))
            )
            doc_link = first_row.find_element(By.CSS_SELECTOR, 'form input[type="image"]')
            
            # Store the current window handle
            main_window = self.driver.current_window_handle
            
            # Click the link (opens new window)
            doc_link.click()
            
            # Switch to the new window
            wait.until(lambda driver: len(driver.window_handles) > 1)
            for window_handle in self.driver.window_handles:
                if window_handle != main_window:
                    self.driver.switch_to.window(window_handle)
                    break

            # Wait for documents table
            docs_table = wait.until(
                EC.presence_of_element_located((By.ID, "case_docs_table"))
            )

            # Find Initial Filing row
            self.st.write("Looking for Initial Filing document...")
            rows = docs_table.find_elements(By.TAG_NAME, "tr")
            initial_filing_row = None
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 1 and "Initial Filing" in cells[1].text:
                    initial_filing_row = row
                    break

            if not initial_filing_row:
                self.st.error("Could not find Initial Filing document")
                return None

            # Click the PDF link
            pdf_link = initial_filing_row.find_element(By.CSS_SELECTOR, 'form input[type="image"]')
            pdf_link.click()

            # Switch to PDF window
            wait.until(lambda driver: len(driver.window_handles) > 2)
            pdf_window = [handle for handle in self.driver.window_handles 
                         if handle != main_window and handle != self.driver.current_window_handle][0]
            self.driver.switch_to.window(pdf_window)

            # Wait for PDF to load and get content
            time.sleep(2)  # Give PDF time to load
            pdf_content = self.driver.page_source

            # Clean up browser resources
            self.cleanup()

            # Return PDF as BytesIO object
            return io.BytesIO(pdf_content.encode('utf-8'))

        except Exception as e:
            self.st.error(f"Error scraping court website: {str(e)}")
            import traceback
            self.st.error(f"Traceback: {traceback.format_exc()}")
            self.cleanup()
            return None

    def analyze_pdf(self, pdf_content):
        """Analyze a PDF file (either from scraping or upload)"""
        # Add your PDF analysis logic here
        pass
