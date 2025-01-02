# streamlit_app.py
import streamlit as st
import json
from datetime import datetime, timedelta

# Import core services
from pdf_service import extract_text_with_textract
from address_service import extract_address
from analysis_service import analyze_text_with_openai
from map_service import get_coordinates, display_map
from ui_components import setup_page, show_app_description
# from court_scraper_headless import CourtScraperHeadless

# Optional Zillow integration
# from zestimate_service import get_zestimate_data
# from property_service import get_property_data
# from display_utils import display_property_data

def process_document(text):
    """Process document text and return analysis"""
    with st.spinner('Analyzing document content with AI...'):
        analysis = analyze_text_with_openai(text)
        
        if analysis:
            st.write("### Analysis Results")
            st.markdown(analysis)
            return analysis
    return None

def process_address(analysis):
    """Extract and process address information"""
    with st.spinner('Extracting property information...'):
        address_info = extract_address(analysis)
        
        if address_info and address_info.get('street_address') != 'NOT_FOUND':
            return address_info
        else:
            st.error("Could not extract valid address from the document.")
            return None

def display_results(analysis, address_info):
    """Display results and map"""
    # Get coordinates for the map
    with st.spinner('Fetching property location...'):
        coordinates = get_coordinates(
            address_info['street_address'],
            address_info['city'],
            address_info['state'],
            address_info['zip_code']
        )
        
        if coordinates:
            # Display the map
            display_map(coordinates)
            
            # Create analysis download
            complete_analysis = (
                f"{analysis}\n\n"
                f"Property Location:\n"
                f"Address: {coordinates['formatted_address']}\n"
                f"Latitude: {coordinates['lat']}\n"
                f"Longitude: {coordinates['lng']}"
            )
            
            st.download_button(
                label="Download Analysis",
                data=complete_analysis,
                file_name="foreclosure_analysis.txt",
                mime="text/plain"
            )

def process_pdf(pdf_data, button_key="analyze"):
    """Process PDF data regardless of source"""
    if 'extracted_text' not in st.session_state:
        with st.spinner('Processing PDF with Amazon Textract...'):
            st.session_state.extracted_text = extract_text_with_textract(pdf_data)
    
    if st.session_state.extracted_text:
        # Show extracted text in expandable section
        with st.expander("View Extracted Text"):
            st.text(st.session_state.extracted_text)
        
        # Process with OpenAI
        if st.button("Analyze Document", key=button_key):
            analysis = process_document(st.session_state.extracted_text)
            if analysis:
                address_info = process_address(analysis)
                if address_info:
                    display_results(analysis, address_info)

def main():
    show_app_description()
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["Upload PDF", "Fetch from Court Website"])
    
    with tab1:
        # File uploader
        uploaded_file = st.file_uploader("Upload a foreclosure document (PDF)", type="pdf")
        
        if uploaded_file is not None:
            process_pdf(uploaded_file, "analyze_uploaded")
    
    with tab2:
        st.subheader("Fetch Recent Foreclosure Document")
        
        # Date inputs
        col1, col2 = st.columns(2)
        with col1:
            default_begin_date = (datetime.now() - timedelta(days=5)).strftime("%m/%d/%Y")
            begin_date = st.text_input("Begin Date (MM/DD/YYYY)", value=default_begin_date)
        
        with col2:
            end_date = st.text_input("End Date (MM/DD/YYYY)", 
                                   value=datetime.now().strftime("%m/%d/%Y"))
        
# In the tab2 section of main():
        # if st.button("Fetch Latest Foreclosure"):
        #     with st.spinner("Fetching document from court website..."):
        #         try:
        #             st.info("Starting court website scraping process...")
        #             scraper = CourtScraperHeadless(st)
        #             pdf_data = scraper.search_foreclosures(begin_date, end_date)
                    
        #             if pdf_data:
        #                 st.success("Document fetched successfully!")
        #                 process_pdf(pdf_data, "analyze_fetched")
        #             else:
        #                 st.error("Could not fetch document. Check the detailed logs above for more information.")
        #         finally:
        #             # Make sure to clean up browser resources
        #             scraper.cleanup()

    # Add a clear button to allow processing a new document
    if 'extracted_text' in st.session_state:
        if st.button("Clear and Process New Document"):
            del st.session_state.extracted_text
            st.rerun()

if __name__ == "__main__":
    setup_page()
    main()
