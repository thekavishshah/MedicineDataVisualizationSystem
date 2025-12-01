import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "medicines_data",
    "user": "postgres",
    "password": "rsoni11"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

class get_cursor:
    def __enter__(self):
        self.conn = get_connection()
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

def test_connection():
    with get_cursor() as cur:
        cur.execute("SELECT 1;")
        return {"status": "ok"}
