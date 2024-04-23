import psycopg2
from psycopg2 import extras

class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.con = None
        self.cur = None

    def __enter__(self):
        self.con = psycopg2.connect(self.database_url)
        self.cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.close()

    def create_table(self):
        create_table_query = """
    CREATE TABLE IF NOT EXISTS quotes (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        rating INTEGER DEFAULT 0,
        price NUMERIC DEFAULT 0.0, -- Ensure this line is included
        tags TEXT DEFAULT '',
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
        self.cur.execute(create_table_query)
        self.con.commit()
        self.setup_trigger_and_function()



    def setup_trigger_and_function(self):
        # Obtain an advisory lock
        self.cur.execute("SELECT pg_advisory_lock(123456789);")
        try:
            self.create_or_replace_function()
            self.create_or_replace_trigger()
        finally:
            # Always release the lock
            self.cur.execute("SELECT pg_advisory_unlock(123456789);")

    def create_or_replace_function(self):
        update_timestamp_function = """
        CREATE OR REPLACE FUNCTION update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
        self.cur.execute(update_timestamp_function)
        self.con.commit()

    def create_or_replace_trigger(self):
        drop_trigger_query = """
        DROP TRIGGER IF EXISTS update_quote_timestamp ON quotes;
        """
        self.cur.execute(drop_trigger_query)
        trigger_query = """
        CREATE TRIGGER update_quote_timestamp
        BEFORE UPDATE ON quotes
        FOR EACH ROW
        EXECUTE FUNCTION update_timestamp();
        """
        self.cur.execute(trigger_query)
        self.con.commit()

    def truncate_table(self):
        self.cur.execute("TRUNCATE TABLE quotes RESTART IDENTITY;")
        self.con.commit()

    def insert_quote(self, quote):
        insert_quote_query = """
        INSERT INTO quotes (content, author, tags, rating, price) VALUES (%s, %s, %s, %s, %s)
        """
        self.cur.execute(insert_quote_query, (quote['content'], quote['author'], quote['tags'], quote['rating'], quote['price']))
        self.con.commit()

    def add_price_column(self):
        try:
            add_column_query = "ALTER TABLE quotes ADD COLUMN price NUMERIC DEFAULT 0.0;"
            self.cur.execute(add_column_query)
            self.con.commit()
        except Exception as e:
            print("Error updating table schema:", e)
            self.con.rollback()
