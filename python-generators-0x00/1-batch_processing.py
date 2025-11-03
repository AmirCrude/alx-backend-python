#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data table in batches.
    Each batch contains at most batch_size rows.
    """
    conn = mysql.connector.connect(
        host="localhost",
        user="root",        # Replace with your MySQL username
        password="Amir&mysql_1738",        # Replace with your MySQL password
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    while True:
        batch = cursor.fetchmany(batch_size)  # fetch batch_size rows
        if not batch:
            break
        yield batch

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """
    Process users in batches and filter users over age 25.
    Prints each user dictionary that meets the condition.
    """
    for batch in stream_users_in_batches(batch_size):  # 1 loop
        for user in batch:  # 2nd loop
            if user['age'] > 25:  # filter condition
                print(user)
