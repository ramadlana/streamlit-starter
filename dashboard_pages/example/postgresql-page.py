import pandas as pd
import streamlit as st
from sqlalchemy import text

from app_db import get_sql_engine

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    with get_sql_engine().connect() as conn:
        result = conn.execute(
            text("SELECT id, name, email FROM dummydata ORDER BY id LIMIT 100")
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df



st.set_page_config(layout="wide")
st.title("PostgreSQL Admin Panel")

df = load_data()

# Display st.dataframe(df, use_container_width=True)
st.table(df)
