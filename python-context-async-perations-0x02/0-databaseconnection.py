#!/usr/bin/python3
"""
Custom class-based context manager for database connections.
"""

import sqlite3


class DatabaseConnection:
    """
    Context manager that handles opening and closing a SQLite database connection.
    """

    def __init__(self, db_name):
        """Initialize with the database file name."""
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        """Establish the database connection."""
        self.connection = sqlite3.connect(self.db_name)
        return self.connection  # Returned value is assigned to variable in 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the database connection is closed."""
        if self.connection:
            self.connection.close()
        # Returning False lets Python re-raise any exceptions that occur inside the with block
        return False


# ==== Example usage ====
if __name__ == "__main__":
    # Replace with your actual database file name
    db_file = "users.db"

    # Using the custom context manager to query all users
    with DatabaseConnection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        results = cursor.fetchall()

        print("User Records:")
        for row in results:
            print(row)
