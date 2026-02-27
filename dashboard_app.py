import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")


# Page Definitions
home_page = st.Page("dashboard_pages/home.py", title="Home", icon=":material/home:")

basic_page = st.Page("dashboard_pages/example/basic.py", title="Basic Page",icon=":material/add_circle:")

map_page = st.Page("dashboard_pages/example/map.py", title="Map Page", icon=":material/delete:")

streamlit_components_page = st.Page("dashboard_pages/example/streamlit-components.py", title="Streamlit Components", icon=":material/dashboard:")

sales_dashboard_page = st.Page("dashboard_pages/example/sales-dashboard.py", title="Sales Dashboard", icon=":material/monitoring:")


# Navigation
pg = st.navigation(
    {
        "Main Menu": [home_page],
        "Example": [basic_page,streamlit_components_page, map_page, sales_dashboard_page],
    }
)

st.set_page_config(page_title="App Name", page_icon=":material/home:")
pg.run()
