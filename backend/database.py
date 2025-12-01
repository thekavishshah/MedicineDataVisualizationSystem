"""
Database connection module for MDVS
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "medicine_data",
    "user": "postgres",
    "password": "Craigers31!"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def test_connection():
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM medicine")
            medicine_count = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM manufacturer")
            manufacturer_count = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM category")
            category_count = cursor.fetchone()["count"]
            
            return {
                "status": "connected",
                "medicines": medicine_count,
                "manufacturers": manufacturer_count,
                "categories": category_count
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}