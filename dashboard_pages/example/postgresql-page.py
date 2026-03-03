

# import os

# import pandas as pd
# import streamlit as st
# from sqlalchemy import create_engine, text

# # ===============================
# # DATABASE CONFIG (ENV VARIABLES)
# # ===============================
# DATABASE_URL = (
#     f"postgresql+psycopg2://"
#     f"{os.environ['DB_USER']}:"
#     f"{os.environ['DB_PASSWORD']}@"
#     f"{os.environ['DB_HOST']}:"
#     f"{os.environ['DB_PORT']}/"
#     f"{os.environ['DB_NAME']}"
# )

# engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10, pool_pre_ping=True)


# # ===============================
# # LOAD DATA (CACHED)
# # ===============================
# @st.cache_data
# def load_data():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM dummydata ORDER BY id LIMIT 100"))
#         df = pd.DataFrame(result.fetchall(), columns=result.keys())
#     return df


# # ===============================
# # UPDATE FUNCTION
# # ===============================
# def update_row(row_id, name, email):
#     with engine.begin() as conn:
#         conn.execute(
#             text("""
#                 UPDATE dummydata
#                 SET name = :name,
#                     email = :email
#                 WHERE id = :id
#             """),
#             {"id": row_id, "name": name, "email": email},
#         )
#     load_data.clear()

# # delete function
# def delete_row(row_id):
#     with engine.begin() as conn:
#         conn.execute(
#             text("DELETE FROM dummydata WHERE id = :id"),
#             {"id": row_id},
#         )
#     load_data.clear()

# # ===============================
# # UI
# # ===============================
# st.set_page_config(layout="wide")
# st.title("PostgreSQL Admin Panel")

# df = load_data()

# # ===============================
# # TABLE VIEW
# # ===============================
# col1, col2 = st.columns([2, 1])

# with col1:
#     st.subheader("Data Table")
#     st.dataframe(df, use_container_width=True)

# with col2:
#     st.subheader("Edit Record")

#     if df.empty:
#         st.info("No data found.")
#         st.stop()

#     selected_id = st.selectbox("Select ID", df["id"], key="select_id")

#     row_data = df[df["id"] == selected_id].iloc[0]

#     with st.form("edit_form", clear_on_submit=False):
#         name = st.text_input("Name", value=row_data["name"])
#         email = st.text_input("Email", value=row_data["email"])

#         col_save, col_cancel = st.columns(2)
#         save = col_save.form_submit_button("Save")
#         cancel = col_cancel.form_submit_button("Delete")

#         if save:
#             update_row(selected_id, name, email)
#             st.success("Updated successfully.")
#             st.rerun()

#         if cancel:
#             delete_row(selected_id)
#             st.success("Deleted successfully.")
#             st.rerun()

import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

# ===============================
# DATABASE CONFIG
# ===============================
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.environ['DB_USER']}:"
    f"{os.environ['DB_PASSWORD']}@"
    f"{os.environ['DB_HOST']}:"
    f"{os.environ['DB_PORT']}/"
    f"{os.environ['DB_NAME']}"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    with engine.connect() as conn:
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

