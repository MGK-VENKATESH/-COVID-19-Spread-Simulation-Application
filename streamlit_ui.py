import streamlit as st
import pandas as pd
import os
from datetime import datetime
import assignment2

# Read the countries data
@st.cache_data
def load_countries():
    return pd.read_csv('a2-countries.csv')

countries_data = load_countries()

# Set up the Streamlit UI
st.title("COVID-19 Simulation App")

# Sample Ratio input
SAMPLE_RATIO = st.number_input("Sample Ratio", min_value=1e4, max_value=1e7, value=1e6, step=1e5, format="%.0f")

# Date inputs
START_DATE = st.date_input("Start Date", datetime(2021, 4, 1))
END_DATE = st.date_input("End Date", datetime(2022, 4, 30))

# Countries dropdown
SELECTED_COUNTRIES = st.multiselect(
    "Select Countries",
    options=countries_data['country'].tolist(),
    default=['Afghanistan', 'Sweden', 'Japan']
)

# Run button
if st.button("Run Simulation"):
    if len(SELECTED_COUNTRIES) > 0:
        with st.spinner('Running simulation...'):
            assignment2.run(
                countries_csv_name='a2-countries.csv',
                countries=SELECTED_COUNTRIES,
                sample_ratio=SAMPLE_RATIO,
                start_date=START_DATE.strftime('%Y-%m-%d'),
                end_date=END_DATE.strftime('%Y-%m-%d')
            )
        st.success('Simulation completed!')
        
        # Display the generated image
        if os.path.exists('a2-covid-simulation.png'):
            st.image('a2-covid-simulation.png')
        else:
            st.error("The simulation image was not generated. Please check the logs for errors.")
    else:
        st.error("Please select at least one country before running the simulation.")

# Display additional information
st.sidebar.header("About")
st.sidebar.info(
    "This app simulates the spread of COVID-19 in selected countries. "
    "Adjust the parameters and select countries to run different scenarios."
)

st.sidebar.header("Instructions")
st.sidebar.info(
    "1. Set the Sample Ratio (lower values for finer simulations, but slower)\n"
    "2. Choose Start and End dates for the simulation\n"
    "3. Select one or more countries from the dropdown\n"
    "4. Click 'Run Simulation' to start\n"
    "5. Wait for the results to be displayed"
)