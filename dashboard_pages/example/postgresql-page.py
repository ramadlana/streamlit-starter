import psycopg2
import streamlit as st

# Connect to PostgreSQL
conn = psycopg2.connect(host="", database="", user="", password="")

# Query data
cur = conn.cursor()
cur.execute("SELECT * FROM ")
rows = cur.fetchall()

# Display data
st.table(rows)

# Close connection
conn.close()
