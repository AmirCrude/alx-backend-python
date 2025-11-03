#!/usr/bin/python3
import sqlite3
import functools

# ==== Decorator to handle database connections ====
def with_db_connection(func):
    """
    Decorator that automatically opens a SQLite database connection,
    passes it to the function, and closes it afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # Open the connection
            conn = sqlite3.connect('users.db')

            # Call the original function, passing the connection as first argument
            return func(conn, *args, **kwargs)

        finally:
            # Ensure connection is closed no matter what
            if conn:
                conn.close()

    return wrapper


# ==== Function using the decorator ====
@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


# ==== Fetch user by ID ====
if __name__ == "__main__":
    user = get_user_by_id(user_id=1)
    print(user)
