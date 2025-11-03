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
            conn = sqlite3.connect('users.db')
            return func(conn, *args, **kwargs)
        finally:
            if conn:
                conn.close()
    return wrapper


# ==== Decorator to manage transactions ====
def transactional(func):
    """
    Decorator to wrap a database function in a transaction.
    Commits if successful; rolls back if an exception occurs.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()   # commit if no errors
            return result
        except Exception as e:
            conn.rollback()  # rollback on error
            print(f"Transaction failed: {e}")
            raise  # re-raise the exception
    return wrapper


# ==== Function using both decorators ====
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)
    )


# ==== Update user's email ====
if __name__ == "__main__":
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    print("User email updated successfully.")
