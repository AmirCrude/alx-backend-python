#!/usr/bin/python3
import sqlite3
import functools

# ==== decorator to log SQL queries ====
def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the SQL query (first positional argument)
        if args:
            print(f"Executing query: {args[0]}")
        elif 'query' in kwargs:
            print(f"Executing query: {kwargs['query']}")

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
