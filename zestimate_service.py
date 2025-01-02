# zestimate_service.py
import requests
import streamlit as st

def get_zestimate_data(address, city, state, zip_code):
    """Get Zestimate data from Bridge Data Output API"""
    try:
        base_url = "https://api.bridgedataoutput.com/api/v2/zestimates_v2/zestimates"
        
        # Format the full address with quotes
        full_address = f'"{address}, {city}, {state} {zip_code}"'
        
        params = {
            'access_token': st.secrets['BRIDGE_API_KEY'],
            'address': full_address
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('bundle'):
            return None
        
        zestimate = data['bundle'][0]
        
        # Format the Zestimate data with required disclaimers
        zestimate_info = {
            "disclaimer": "Data provided 'as is' via the Zestimate API",
            "copyright": "© Zillow, Inc., 2006-2024. Use is subject to Terms of Use",
            "zestimate_label": "Zestimate® home valuation",
            "zillow_url": zestimate.get('zillowUrl', 'N/A'),
            "values": {
                "Current Zestimate": zestimate.get('zestimate', 'N/A'),
                "30-Day Change": zestimate.get('minus30', 'N/A'),
                "Value Range": {
                    "Low": zestimate.get('zestimate', 0) * (1 - zestimate.get('lowPercent', 0)/100) if zestimate.get('zestimate') else 'N/A',
                    "High": zestimate.get('zestimate', 0) * (1 + zestimate.get('highPercent', 0)/100) if zestimate.get('zestimate') else 'N/A'
                },
                "Rental Estimate": zestimate.get('rentalZestimate', 'N/A'),
                "Rental Range": {
                    "Low": zestimate.get('rentalZestimate', 0) * (1 - zestimate.get('rentalLowPercent', 0)/100) if zestimate.get('rentalZestimate') else 'N/A',
                    "High": zestimate.get('rentalZestimate', 0) * (1 + zestimate.get('rentalHighPercent', 0)/100) if zestimate.get('rentalZestimate') else 'N/A'
                }
            },
            "Last Updated": zestimate.get('timestamp', 'N/A')
        }
        
        return zestimate_info
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Zestimate data: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response text: {e.response.text}")
        return None
