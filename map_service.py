# map_service.py
import streamlit as st
from streamlit_folium import folium_static
import folium
import requests

def get_coordinates(address, city, state, zip_code):
    """Get latitude and longitude from address using Google Geocoding API"""
    try:
        # Format the address
        full_address = f"{address}, {city}, {state} {zip_code}"
        
        # Make request to Google Geocoding API
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": full_address,
            "key": st.secrets["GOOGLE_MAPS_API_KEY"]
        }
        
        # Debug information
        st.write("Requesting coordinates for:", full_address)
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Debug information
        st.write("Google API Response Status:", data["status"])
        
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "formatted_address": data["results"][0]["formatted_address"]
            }
        else:
            st.error(f"Geocoding error: {data['status']}")
            return None
            
    except Exception as e:
        st.error(f"Error getting coordinates: {str(e)}")
        return None

def display_map(coordinates, property_info=None):
    """Display an interactive map with the property location"""
    try:
        # Create a map centered on the property
        m = folium.Map(
            location=[coordinates["lat"], coordinates["lng"]], 
            zoom_start=15,
            width=800,
            height=500
        )
        
        # Add a marker for the property
        tooltip = coordinates["formatted_address"]
        
        folium.Marker(
            [coordinates["lat"], coordinates["lng"]],
            popup=folium.Popup(tooltip, max_width=300),
            tooltip="Click for details",
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)
        
        # Add the map to Streamlit
        st.write("### Property Location")
        folium_static(m)
        
        # Display the formatted address
        st.write(f"**Formatted Address:** {coordinates['formatted_address']}")
        
    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")
