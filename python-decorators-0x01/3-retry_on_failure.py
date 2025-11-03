#!/usr/bin/python3
import time
import sqlite3
import functools

# ==== Decorator to handle database connections ====
def with_db_connection(func):
    """
    Automatically opens a SQLite database connection,
    passes it to the function, and closes it afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            return func(conn, *args, **kwargs)
        finally:
            if conn:
                conn.close()
    return wrapper


# ==== Decorator to retry on failure ====
def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function if an exception occurs.
    Arguments:
        retries: number of retry attempts
        delay: wait time in seconds between attempts
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < retries:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
            # If all retries fail, raise the last exception
            raise last_exception
        return wrapper
    return decorator


# ==== Function using both decorators ====
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# ==== Attempt to fetch users with retry ====
if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)
