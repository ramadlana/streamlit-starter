import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# st.markdown("""
# <style>
#     header { visibility: hidden; height: 0; }

#     #MainMenu { visibility: hidden; }

#     footer { visibility: hidden; }

#     button[kind="header"] { display: none !important; }

#     .block-container { padding-top: 0.75rem !important; }
#     button[aria-label="Collapse sidebar"] { display: none !important; }
# </style>
# """, unsafe_allow_html=True)


home_page = st.Page("home.py", title="Home", icon=":material/home:")

basic_page = st.Page("basic.py", title="Basic Page",
                     icon=":material/add_circle:")

map_page = st.Page("map.py", title="Map Page",
                   icon=":material/delete:")

basic_nested = st.Page(
    "example/examplebasic.py", title="Basic Nested Page", icon=":material/delete:")  # make as home page

pg = st.navigation(
    {
        "Main Menu": [home_page, map_page],
        "Example": [basic_nested, basic_page],
    }
)

st.set_page_config(page_title="App Name", page_icon=":material/home:")
pg.run()
