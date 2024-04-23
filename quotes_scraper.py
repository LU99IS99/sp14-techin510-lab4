import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import argparse

from db import Database

# Load environment variables
load_dotenv()

# Base URL for the scraping
BASE_URL = 'https://books.toscrape.com/catalogue/page-{page}.html'

# Initialize the command-line argument parser
parser = argparse.ArgumentParser(description="Scrape books from 'Books to Scrape'.")
parser.add_argument('--truncate', action='store_true', help='Truncate the table before inserting new records')
args = parser.parse_args()

# Connect to the database using a context manager
with Database(os.getenv('DATABASE_URL')) as db:
    # Create a table if it doesn't exist
    db.create_table()
    
    # Optionally truncate table if specified in command line args
    if args.truncate:
        db.truncate_table()
    
    # Initialize a list to store books
    books = []
    page = 1
    
    while True:
        url = BASE_URL.format(page=page)
        print(f"Scraping {url}")
        
        # Make a request to the webpage
        response = requests.get(url)
        
        # Check if the current page is empty of book listings
        if 'No books found!' in response.text:
            break
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all book containers
        book_containers = soup.find_all('article', class_='product_pod')
        
        if not book_containers:
            break  # If no books are found, exit the loop
        
        for book in book_containers:
            # Extract details for each book
            title = book.h3.a['title']
            price = book.find('p', class_='price_color').text[2:]  # Remove the pound symbol
            rating = book.p['class'][1]  # Ratings class returns ['star-rating', 'Three'] for example
            book_details = {
                'title': title,
                'price': price,
                'rating': rating
            }
            
            # Insert book into the database
            db.insert_book(book_details)
            books.append(book_details)
        
        # Go to the next page
        page += 1

    # Optionally print all books
    print(books)
