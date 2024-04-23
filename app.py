import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from db import Database

load_dotenv()

def search_and_filter(db, search_query, sort_by, sort_order):
    query = """
    SELECT * FROM quotes
    WHERE content ILIKE %s OR author ILIKE %s
    ORDER BY {} {};
    """.format(sort_by, sort_order)
    return pd.read_sql(query, db.con, params=(f'%{search_query}%', f'%{search_query}%'))

# Establish a database connection using a context manager
with Database(os.getenv('DATABASE_URL')) as db:
    db.create_table()

st.title('Quote Generator')

search_query = st.text_input("Search quotes by content or author")
sort_by = st.selectbox("Sort by", options=['price', 'rating'], index=0)
sort_order = st.selectbox("Sort order", options=['ASC', 'DESC'], index=0)

if st.button('Search'):
    with Database(os.getenv('DATABASE_URL')) as db:
        df = search_and_filter(db, search_query, sort_by, sort_order)
    
    if df.empty:
        st.write("No quotes found.")
    else:
        st.write(df)

# Optional feature to refresh or reload quotes
if st.button("Reload Quotes"):
    st.experimental_rerun()
