#!/usr/bin/python3
import time
import sqlite3
import functools

# Global dictionary to store cached query results
query_cache = {}

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


# ==== Decorator to cache query results ====
def cache_query(func):
    """
    Caches database query results based on the SQL query string.
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Check if the query result is already cached
        if query in query_cache:
            print("Using cached result...")
            return query_cache[query]

        # Execute the original function and cache the result
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        print("Caching result for future calls...")
        return result

    return wrapper


# ==== Function using both decorators ====
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# ==== Example usage ====
if __name__ == "__main__":
    # First call - executes query and caches result
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)

    # Second call - uses cached result
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
