#!/usr/bin/python3
"""
Reusable context manager to execute database queries safely.
"""

import sqlite3


class ExecuteQuery:
    """
    Context manager that handles database connection and query execution.
    """

    def __init__(self, db_name, query, params=None):
        """
        Initialize with the database name, SQL query, and optional parameters.
        """
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.connection = None
        self.results = None

    def __enter__(self):
        """
        Establish the database connection and execute the query.
        Returns the query results.
        """
        self.connection = sqlite3.connect(self.db_name)
        cursor = self.connection.cursor()

        # Execute the provided query with parameters (if any)
        cursor.execute(self.query, self.params)
        self.results = cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensure the database connection is closed.
        """
        if self.connection:
            self.connection.close()
        # Returning False allows any exceptions to propagate
        return False


# ==== Example usage ====
if __name__ == "__main__":
    db_file = "users.db"
    sql_query = "SELECT * FROM users WHERE age > ?"
    parameter = (25,)

    with ExecuteQuery(db_file, sql_query, parameter) as result:
        print("Users older than 25:")
        for row in result:
            print(row)
