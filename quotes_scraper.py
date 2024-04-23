import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from db import Database  # 确保你有一个处理数据库的模块


def get_price(s) -> float:
    return float(s.replace('Â£', ''))


def get_rating(s) -> int:
    if s == 'One':
        return 1
    elif s == 'Two':
        return 2
    elif s == 'Three':
        return 3
    elif s == 'Four':
        return 4
    elif s == 'Five':
        return 5


def get_availability(s) -> bool:
    if s == 'In stock':
        return True
    return False


load_dotenv()
BASE_URL = 'https://books.toscrape.com/catalogue/page-{page}.html'
DETAIL_URL = 'https://books.toscrape.com/catalogue'  # 基本URL用于拼接详情页

with Database(os.getenv('DATABASE_URL')) as pg:
    pg.create_table()  # 确保这个方法可以创建适合新数据的表
    pg.truncate_table()
    books = []
    page = 1
    while True:
        url = BASE_URL.format(page=page)
        print(f"Scraping {url}")
        response = requests.get(url)

        if response.status_code == 404:
            print("Reached end of pages.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        book_items = soup.select('ol.row > li')

        if not book_items:
            print("No books found, end of pages.")
            break

        for item in book_items:
            book = {}
            book['title'] = item.select_one('h3 a')['title']
            book['price'] = get_price(item.select_one('p.price_color').text)
            book['rating'] = get_rating(item.select_one('p.star-rating')['class'][1])
            book['availability'] = get_availability(item.select_one('p.instock').text.strip())

            # Navigate to book detail page
            relative_link = item.select_one('h3 a')['href']
            detail_link = f"{DETAIL_URL}/{relative_link}"
            detail_response = requests.get(detail_link)
            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

            # Extract detailed info
            book['description'] = detail_soup.select_one('div#product_description ~ p').text if detail_soup.select_one(
                'div#product_description ~ p') else 'No description'
            book['product_type'] = detail_soup.select_one('table.table.table-striped tr:nth-of-type(2) > td').text
            book['reviews'] = detail_soup.select_one('table.table.table-striped tr:nth-of-type(7) > td').text

            # insert into database
            pg.insert_book(book)
            books.append(book)
            print(book)
        page += 1
print('finished')