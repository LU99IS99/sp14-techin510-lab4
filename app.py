import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from db import Database

# Load environment variables
load_dotenv()

# Reference for pagination: https://medium.com/streamlit/paginating-dataframes-with-streamlit-2da29b080920
def paginate_dataframe(input_df, rows_per_page):
    """Splits a DataFrame into smaller DataFrames to handle pagination."""
    return [
        input_df.iloc[i: i + rows_per_page] for i in range(0, len(input_df), rows_per_page)
    ]

# Establish a database connection using a context manager
with Database(os.getenv('DATABASE_URL')) as db:
    db.create_table()
    # Retrieve all quotes from the database
    query = 'SELECT * FROM quotes'
    df = pd.read_sql(query, db.con)

# Streamlit application start
st.title('Quote Generator')

# Pagination control
total_pages = (len(df) // batch_size) + (len(df) % batch_size > 0)
batch_size = st.sidebar.selectbox("Page Size", options=[25, 50, 100], index=0)
current_page = st.sidebar.number_input("Page Number", min_value=1, max_value=total_pages, step=1, value=1)

# Create a container for the DataFrame
container = st.container()
with container:
    if df.empty:
        st.write("No quotes available.")
    else:
        # Display the current page of quotes
        pages = paginate_dataframe(df, batch_size)
        st.dataframe(pages[current_page - 1], use_container_width=True)
        st.markdown(f"Page **{current_page}** of **{total_pages}**")

# Optional feature to refresh or reload quotes
if st.button("Reload Quotes"):
    st.experimental_rerun()
