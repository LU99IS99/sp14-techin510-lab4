import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from db import Database

# Load environment variables
load_dotenv()

def paginate_dataframe(input_df, rows_per_page):
    """Splits a DataFrame into smaller DataFrames to handle pagination."""
    return [
        input_df.iloc[i: i + rows_per_page] for i in range(0, len(input_df), rows_per_page)
    ]

# Establish a database connection using a context manager
with Database(os.getenv('DATABASE_URL')) as db:
    db.create_table()

    # Search and filter setup
    search_query = st.sidebar.text_input("Search by name or description")
    filter_rating = st.sidebar.slider("Minimum rating", 0, 5, 1)
    sort_option = st.sidebar.selectbox("Sort by", ['Rating', 'Price'], index=0)
    sort_order = 'ASC' if st.sidebar.radio("Sort order", ['Ascending', 'Descending']) == 'Ascending' else 'DESC'

    # Dynamic SQL query based on user input
    query = f'''
    SELECT * FROM books
    WHERE (title ILIKE %s OR description ILIKE %s) AND rating >= %s
    ORDER BY {sort_option.lower()} {sort_order};
    '''
    df = pd.read_sql(query, db.con, params=(f'%{search_query}%', f'%{search_query}%', filter_rating))

st.title('Book Finder')

if not df.empty:
    batch_size = st.sidebar.selectbox("Page Size", options=[25, 50, 100], index=0)
    total_pages = (len(df) // batch_size) + (len(df) % batch_size > 0)
    current_page = st.sidebar.number_input("Page Number", min_value=1, max_value=total_pages, step=1, value=1, format="%d") if total_pages > 0 else 1

    # Display books with pagination
    pages = paginate_dataframe(df, batch_size)
    container = st.container()
    with container:
        if total_pages > 0:
            st.dataframe(pages[current_page - 1], use_container_width=True)
            st.markdown(f"Page **{current_page}** of **{total_pages}**")
        else:
            st.write("No pages to display.")
else:
    st.write("No books found matching the criteria.")

# Optional feature to refresh or reload the data
if st.button("Reload Data"):
    st.experimental_rerun()
