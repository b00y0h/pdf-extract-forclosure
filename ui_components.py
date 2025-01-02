# ui_components.py
import streamlit as st

def setup_page():
    """Setup page configuration and styling"""
    st.set_page_config(
        page_title="Foreclosure Document Analysis App",
        page_icon="🏠",
        layout="wide"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

def show_app_description():
    """Display app description"""
    st.title("Foreclosure Document Analysis App")
    
    st.markdown("""
    This app analyzes foreclosure documents to extract key information including:
    - Property details and address
    - Claims and judgements
    - Owner/plaintiff information
    - Liens and encumbrances
    - Risk factors and red flags
    """)
