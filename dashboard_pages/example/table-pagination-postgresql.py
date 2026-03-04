import math
import pandas as pd
import streamlit as st
from sqlalchemy import text
from app_db import get_sql_engine

PAGE_SIZE = 20

@st.cache_data(ttl=60)
def get_total_rows(search: str | None):
    with get_sql_engine().connect() as conn:
        if search:
            result = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM dummydata
                    WHERE name ILIKE :search
                       OR email ILIKE :search
                """),
                {"search": f"%{search}%"},
            )
        else:
            result = conn.execute(
                text("SELECT COUNT(*) FROM dummydata")
            )

        return result.scalar()


@st.cache_data(ttl=60)
def load_table_1(page: int, search: str | None):
    offset = (page - 1) * PAGE_SIZE

    with get_sql_engine().connect() as conn:
        if search:
            result = conn.execute(
                text("""
                    SELECT id, name, email
                    FROM dummydata
                    WHERE name ILIKE :search
                       OR email ILIKE :search
                    ORDER BY id
                    LIMIT :limit OFFSET :offset
                """),
                {
                    "search": f"%{search}%",
                    "limit": PAGE_SIZE,
                    "offset": offset,
                },
            )
        else:
            result = conn.execute(
                text("""
                    SELECT id, name, email
                    FROM dummydata
                    ORDER BY id
                    LIMIT :limit OFFSET :offset
                """),
                {
                    "limit": PAGE_SIZE,
                    "offset": offset,
                },
            )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df

st.set_page_config(layout="wide")

st.title("PostgreSQL Admin Panel")

col1, col2 = st.columns([2,1])
with col1:
    search = st.text_input("Search name or email")

    total_rows = get_total_rows(search)
    total_pages = max(1, math.ceil(total_rows / PAGE_SIZE))

with col2:
    page_number = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        step=1,
        value=1,
    )

st.session_state.page_number = page_number


df_table_1 = load_table_1(page_number, search)

st.write(f"Page {page_number} of {total_pages} Total rows: {total_rows}")

st.dataframe(
    df_table_1,
    use_container_width=True,
    hide_index=True,
)



#-------------------------------------
# load data for different table
#-------------------------------------
@st.cache_data(ttl=60)
def load_table_2():
    with get_sql_engine().connect() as conn:
        result = conn.execute(
            text("SELECT id, name, email FROM dummydata ORDER BY id LIMIT :pagesize"),
            {"pagesize": 10},
        )
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

st.title("PostgreSQL Data Normal Table")
df_table_2 = load_table_2()
# Display st.dataframe(df, use_container_width=True)
st.dataframe(df_table_2,use_container_width=True,hide_index=True)
