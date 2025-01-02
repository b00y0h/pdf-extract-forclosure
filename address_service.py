# address_service.py
from openai import OpenAI
import streamlit as st

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_address(text):
    """Extract address from OpenAI analysis"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": r"""Extract the property address from the text and format it into these components:
                    - street_address (number and street name)
                    - city
                    - state (2-letter code)
                    - zip_code (5 digits)
                    Return ONLY these four components in a simple format like this:
                    street_address: 123 Main St
                    city: Springfield
                    state: IL
                    zip_code: 62701
                    If any component is missing, write "NOT_FOUND" for that component."""
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3
        )
        
        # Parse the response
        address_lines = response.choices[0].message.content.strip().split('\n')
        address_dict = {}
        for line in address_lines:
            key, value = line.split(': ', 1)
            address_dict[key.strip()] = value.strip()
        
        return address_dict
        
    except Exception as e:
        st.error(f"Error extracting address: {str(e)}")
        return None
