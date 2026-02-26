import streamlit as st
import pandas as pd


"""
# Plot a map
"""
st.write("#### Single point")
map_data = pd.DataFrame(
    {
        "lat": [
            -6.175392,  # Monas
        ],
        "lon": [
            106.827153,
        ],
    }
)
st.map(map_data)

st.write("#### Multiple point")
map_data = pd.DataFrame(
    {
        "lat": [
            -6.175392,  # Monas
            -6.224722,  # SCBD
            -6.193125,  # Gambir
            -6.261493,  # Blok M
            -6.208763,  # Sudirman
        ],
        "lon": [
            106.827153,
            106.808458,
            106.826970,
            106.810600,
            106.823601,
        ],
    }
)

st.map(map_data)
