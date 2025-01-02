# property_service.py
import requests
import streamlit as st

def get_property_data(address, city, state, zip_code):
    """Get property data from Bridge Data Output API"""
    try:
        # Base URL for Bridge API
        base_url = "https://api.bridgedataoutput.com/api/v2/pub"
        headers = {
            'Authorization': f"Bearer {st.secrets['BRIDGE_API_KEY']}",
            'Accept': 'application/json'
        }
        
        # First, search for the parcel using address
        parcels_url = f"{base_url}/parcels"
        params = {
            'access_token': st.secrets['BRIDGE_API_KEY'],
            'limit': 1,
            'address.full': f"{address}, {city}, {state} {zip_code}"
        }
        
        response = requests.get(parcels_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('bundle', []):
            return "Property not found in database"
            
        parcel = data['bundle'][0]
        parcel_id = parcel.get('id')
        
        # Get assessment history
        assessments_url = f"{base_url}/parcels/{parcel_id}/assessments"
        params = {
            'access_token': st.secrets['BRIDGE_API_KEY'],
            'limit': 5,  # Get last 5 assessments
            'sortBy': 'tax_year',
            'order': 'desc'
        }
        
        assessment_response = requests.get(assessments_url, params=params)
        assessment_response.raise_for_status()
        assessment_data = assessment_response.json()
        
        # Get transaction history
        transactions_url = f"{base_url}/parcels/{parcel_id}/transactions"
        params = {
            'access_token': st.secrets['BRIDGE_API_KEY'],
            'limit': 5,  # Get last 5 transactions
            'sortBy': 'recording_date',
            'order': 'desc'
        }
        
        transaction_response = requests.get(transactions_url, params=params)
        transaction_response.raise_for_status()
        transaction_data = transaction_response.json()
        
        # Format the response
        property_info = {
            "Parcel Information": {
                "Parcel ID": parcel.get('id', 'N/A'),
                "Land Use": parcel.get('land_use', 'N/A'),
                "Total Value": parcel.get('total_value', 'N/A'),
                "Land Value": parcel.get('land_value', 'N/A'),
                "Building Value": parcel.get('building_value', 'N/A'),
                "Living Area": parcel.get('building_area', 'N/A'),
                "Year Built": parcel.get('year_built', 'N/A'),
                "Lot Size": parcel.get('lot_size', 'N/A')
            },
            "Assessment History": [
                {
                    "Year": assessment.get('tax_year', 'N/A'),
                    "Total Value": assessment.get('total_value', 'N/A'),
                    "Tax Amount": assessment.get('tax_amount', 'N/A')
                }
                for assessment in assessment_data.get('bundle', [])
            ],
            "Transaction History": [
                {
                    "Date": transaction.get('recording_date', 'N/A'),
                    "Price": transaction.get('price', 'N/A'),
                    "Type": transaction.get('type', 'N/A')
                }
                for transaction in transaction_data.get('bundle', [])
            ]
        }
        
        return property_info
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching property data: {str(e)}"
