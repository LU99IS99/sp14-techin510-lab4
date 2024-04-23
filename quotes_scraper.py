import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import argparse

from db import Database

# Load environment variables
load_dotenv()

# Base URL for the scraping
BASE_URL = 'https://quotes.toscrape.com/page/{page}/'

# Initialize the command-line argument parser
parser = argparse.ArgumentParser(description="Scrape quotes from 'quotes.toscrape.com'.")
parser.add_argument('--truncate', action='store_true', help='Truncate the table before inserting new records')
args = parser.parse_args()

# Connect to the database using a context manager
with Database(os.getenv('DATABASE_URL')) as pg:
    # Create a table if it doesn't exist
    pg.create_table()
    
    # Optionally truncate table if specified in command line args
    if args.truncate:
        pg.truncate_table()
    
    # Initialize a list to store quotes
    quotes = []
    page = 1
    
    while True:
        url = BASE_URL.format(page=page)
        print(f"Scraping {url}")
        
        # Make a request to the webpage
        response = requests.get(url)
        
        # Check if the page has no quotes, indicating an end or invalid page
        if 'No quotes found!' in response.text:
            break
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all quote containers
        quote_divs = soup.select('div.quote')
        
        for quote_div in quote_divs:
            # Extract details for each quote
            quote = {
                'content': quote_div.select_one('span.text').text,
                'author': quote_div.select_one('small.author').text,
                'tags': ','.join([tag.text for tag in quote_div.select('a.tag')])
            }
            
            # Insert quote into the database
            pg.insert_quote(quote)
            quotes.append(quote)
        
        # Go to the next page
        page += 1

    # Optionally print all quotes
    print(quotes)
