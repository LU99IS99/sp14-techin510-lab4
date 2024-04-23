import psycopg2
from psycopg2 import extras

class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.con = None
        self.cur = None

    def __enter__(self):
        # Establish a database connection and create a cursor
        self.con = psycopg2.connect(self.database_url)
        self.cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Make sure to close the cursor and connection properly
        if self.cur is not None:
            self.cur.close()
        if self.con is not None:
            self.con.close()

    def create_table(self):
        # SQL query to create a table if it does not exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            tags TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        self.cur.execute(create_table_query)
        self.con.commit()

    def truncate_table(self):
        # SQL query to truncate the table
        truncate_table_query = """
        TRUNCATE TABLE quotes RESTART IDENTITY;
        """
        self.cur.execute(truncate_table_query)
        self.con.commit()

    def insert_quote(self, quote):
        # SQL query to insert a new quote
        insert_quote_query = """
        INSERT INTO quotes (content, author, tags) VALUES (%s, %s, %s)
        """
        self.cur.execute(insert_quote_query, (quote['content'], quote['author'], quote['tags']))
        self.con.commit()

    def update_timestamps(self):
        # SQL to update timestamps for existing rows (to demonstrate how to handle 'updated_at')
        update_timestamps_query = """
        UPDATE quotes SET updated_at = CURRENT_TIMESTAMP WHERE id = %s;
        """
        self.cur.execute(update_timestamps_query, (quote_id,))  # Assuming 'quote_id' is defined
        self.con.commit()
