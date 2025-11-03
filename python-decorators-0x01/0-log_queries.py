#!/usr/bin/python3
import sqlite3
import functools
from datetime import datetime


# ==== decorator to log SQL queries ====
def log_queries(func):
    """
    Decorator that logs SQL queries with timestamps before executing them.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determine the query (either positional or keyword argument)
        query = None
        if args:
            query = args[0]
        elif 'query' in kwargs:
            query = kwargs['query']

        # Log the SQL query with a timestamp
        if query:
            print(f"[{timestamp}] Executing query: {query}")
        else:
            print(f"[{timestamp}] No SQL query found to execute.")

        # Execute the original function
        result = func(*args, **kwargs)
        return result

    return wrapper


# ==== Function using the decorator ====
@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# ==== Fetch users while logging the query ====
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)
