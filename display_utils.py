# display_utils.py
import streamlit as st
import pandas as pd
from utils import format_currency

def display_property_data(property_data, zestimate_data):
    """Display property data and Zestimate in a structured format"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Parcel Information
        st.write("#### 🏠 Parcel Information")
        for key, value in property_data["Parcel Information"].items():
            st.write(f"**{key}:** {format_currency(value)}")
    
    with col2:
        # Zestimate Information
        if zestimate_data:
            st.write("#### 💰 Zestimate Data")
            st.write(f"**Current Zestimate:** {format_currency(zestimate_data['Current Zestimate'])}")
            st.write(f"**30-Day Change:** {format_currency(zestimate_data['30-Day Change'])}")
            st.write("**Value Range:**")
            st.write(f"- Low: {format_currency(zestimate_data['Value Range']['Low'])}")
            st.write(f"- High: {format_currency(zestimate_data['Value Range']['High'])}")
            st.write(f"**Monthly Rental Estimate:** {format_currency(zestimate_data['Rental Estimate'])}")
            st.write("**Rental Range:**")
            st.write(f"- Low: {format_currency(zestimate_data['Rental Range']['Low'])}")
            st.write(f"- High: {format_currency(zestimate_data['Rental Range']['High'])}")
            st.write(f"**Last Updated:** {zestimate_data['Last Updated']}")
            st.markdown(f"[View on Zillow]({zestimate_data['Zillow URL']})")
    
    # Assessment History
    st.write("#### 📊 Assessment History")
    if property_data["Assessment History"]:
        assessment_df = pd.DataFrame(property_data["Assessment History"])
        assessment_df = assessment_df.applymap(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
        st.dataframe(assessment_df)
    else:
        st.write("No assessment history available")
    
    # Transaction History
    st.write("#### 📈 Transaction History")
    if property_data["Transaction History"]:
        transaction_df = pd.DataFrame(property_data["Transaction History"])
        transaction_df = transaction_df.applymap(lambda x: format_currency(x) if isinstance(x, (int, float)) else x)
        st.dataframe(transaction_df)
    else:
        st.write("No transaction history available")
