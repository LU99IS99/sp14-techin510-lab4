import time
import psycopg2


class Database:
    def __init__(self, database_url) -> None:
        self.con = psycopg2.connect(database_url)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def create_table(self):
        q = """
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price INT NOT NULL,
            rating FLOAT NOT NULL,
            availability Bool NOT NULL,
            description TEXT NOT NULL,
            product_type TEXT NOT NULL,
            reviews INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.cur.execute(q)
        self.con.commit()

    def truncate_table(self):
        q = """
        TRUNCATE TABLE books
        """
        self.cur.execute(q)
        self.con.commit()

    def insert_book(self, book):
        q = """
        INSERT INTO books (title, price, rating, availability, description, product_type, reviews) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        self.cur.execute(q, (book['title'], book['price'], book['rating'], book['availability'], book['description'], book['product_type'], book['reviews']))
        self.con.commit()