#!/usr/bin/python3
import mysql.connector

def stream_users():
    """
    Generator that streams rows from the user_data table one by one.
    Yields each row as a dictionary.
    """
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Amir&mysql_1738",
            database="ALX_prodev"
        )

        cursor = connection.cursor(dictionary=True)  # So rows come out as dicts
        cursor.execute("SELECT * FROM user_data;")

        # Yield rows one by one
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        # Always close the connection and cursor
        if cursor:
            cursor.close()
        if connection:
            connection.close()


