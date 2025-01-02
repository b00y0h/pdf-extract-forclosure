# court_scraper.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import io
import time

class CourtScraper:
    def __init__(self, streamlit_instance):
        self.base_url = "https://www.courtclerk.org"
        self.session = requests.Session()
        self.session.cookies.clear()  # Clear any existing cookies
        self.st = streamlit_instance
        
        # Add headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })

    def make_request(self, method, url, **kwargs):
        """Make a request with a small delay"""
        time.sleep(1)  # 1 second delay
        if method.lower() == 'get':
            return self.session.get(url, verify=False, **kwargs)
        else:
            return self.session.post(url, verify=False, **kwargs)

    def initialize_session(self):
        """Initialize session by visiting the main page first"""
        try:
            # Visit the main page first to get cookies
            main_page = self.make_request('get', self.base_url)
            if main_page.status_code != 200:
                self.st.error(f"Failed to initialize session: {main_page.status_code}")
                return False
            return True
        except Exception as e:
            self.st.error(f"Error initializing session: {str(e)}")
            return False

    def check_for_cookie_error(self, response):
        """Check if response indicates a cookie error"""
        if 'Error 0626' in response.text or 'cookies are enabled' in response.text:
            self.st.error("Cookie error detected. Reinitializing session...")
            return self.initialize_session()
        return True
        
    def search_foreclosures(self, begin_date, end_date=None):
        """Search foreclosures between dates"""
        try:
            # Initialize session first
            if not self.initialize_session():
                return None

            # If no end date provided, use today
            if not end_date:
                end_date = datetime.now().strftime("%m/%d/%Y")
            
            # Form data for the search
            search_data = {
                "ccode": "A",  # All foreclosure types
                "begdate": begin_date,
                "enddate": end_date,
                "classification": "FORECLOSURE"
            }
            
            # Submit the form directly to the results page
            results_url = f"{self.base_url}/data/cpciv_classification_results.php"
            self.st.write("Submitting search to:", results_url)
            self.st.write("With data:", search_data)
            
            response = self.make_request('post', results_url, data=search_data)
            if not self.check_for_cookie_error(response):
                return None

            self.st.write(f"Search form response status: {response.status_code}")
            
            if response.status_code != 200:
                self.st.error(f"Search form error response: {response.text}")
                return None
            
            # Save the response HTML for debugging
            with self.st.expander("View Search Response HTML"):
                self.st.code(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find results table
            results_table = soup.find('table', id='cpciv_classification_results')
            if not results_table:
                self.st.error("Could not find results table. Response content:")
                self.st.write(soup.prettify())
                return None

            # Get tbody and its first row
            tbody = results_table.find('tbody')
            if not tbody:
                self.st.error("Could not find tbody in results table")
                return None

            first_row = tbody.find('tr')
            if not first_row:
                self.st.error("No results found in table")
                self.st.write("Table content:", results_table.prettify())
                return None

            # Find the document form in the last cell (td) of the first row
            doc_form = first_row.find_all('td')[-1].find('form')  # Get last cell and find form within it
            if not doc_form:
                self.st.error("Could not find document form in first row")
                self.st.write("First row content:", first_row.prettify())
                return None

            # Extract case number
            case_number_input = doc_form.find('input', {'name': 'casenumber'})
            if not case_number_input:
                self.st.error("Could not find case number input")
                self.st.write("Form content:", doc_form.prettify())
                return None

            case_number = case_number_input['value']
            self.st.write(f"Found case number: {case_number}")

            # Submit form to get case documents
            case_docs_url = f"{self.base_url}/data/case_summary.php"  # Add /data/ to the path
            case_docs_data = {
                "sec": "doc",
                "casenumber": case_number
            }            
            self.st.write("Submitting case documents form with data:", case_docs_data)
            docs_response = self.make_request('post', case_docs_url, data=case_docs_data)
            if not self.check_for_cookie_error(docs_response):
                return None

            self.st.write(f"Case documents response status: {docs_response.status_code}")
            
            if docs_response.status_code != 200:
                self.st.error(f"Case documents error response: {docs_response.text}")
                return None
            
            # Save the case documents HTML for debugging
            with self.st.expander("View Case Documents Response HTML"):
                self.st.code(docs_response.text)
            
            docs_soup = BeautifulSoup(docs_response.text, 'html.parser')
            
            # Find documents table
            docs_table = docs_soup.find('table', id='case_docs_table')
            if not docs_table:
                self.st.error("Could not find documents table")
                return None
            
            # Find Initial Filing row
            initial_filing_found = False
            for row in docs_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) > 1 and "Initial Filing" in cells[1].text:
                    initial_filing_found = True
                    self.st.write("Found Initial Filing row")
                    form = cells[-1].find('form')
                    if form:
                        # Extract PDF viewing data
                        try:
                            pdf_data = {
                                "case_number": form.find('input', {'name': 'case_number'})['value'],
                                "path_link": form.find('input', {'name': 'path_link'})['value'],
                                "doc_no": form.find('input', {'name': 'doc_no'})['value'],
                                "must_redact": form.find('input', {'name': 'must_redact'})['value']
                            }
                            
                            self.st.write("Submitting PDF view form with data:", pdf_data)
                            
                            # Get PDF content
                            pdf_url = f"{self.base_url}/data/image_view_stream.php"
                            pdf_response = self.make_request('post', pdf_url, data=pdf_data)
                            if not self.check_for_cookie_error(pdf_response):
                                return None

                            self.st.write(f"PDF response status: {pdf_response.status_code}")
                            self.st.write(f"PDF response headers: {dict(pdf_response.headers)}")
                            
                            if pdf_response.status_code != 200:
                                self.st.error(f"PDF error response: {pdf_response.text}")
                                return None
                            
                            if 'application/pdf' in pdf_response.headers.get('content-type', ''):
                                return io.BytesIO(pdf_response.content)
                            else:
                                self.st.error(f"Unexpected content type: {pdf_response.headers.get('content-type')}")
                                return None
                        except Exception as e:
                            self.st.error(f"Error processing PDF form: {str(e)}")
                            self.st.write("Form content:", form.prettify())
                            return None
            
            if not initial_filing_found:
                self.st.error("Could not find Initial Filing row in documents table")
                self.st.write("Table content:", docs_table.prettify())
            
            return None
            
        except Exception as e:
            self.st.error(f"Error scraping court website: {str(e)}")
            import traceback
            self.st.error(f"Traceback: {traceback.format_exc()}")
            return None
