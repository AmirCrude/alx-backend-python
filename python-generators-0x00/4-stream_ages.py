#!/usr/bin/python3
import mysql.connector

def stream_user_ages():
    """
    Generator that connects to the database and yields each user's age
    one at a time, without loading all data into memory.
    """
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Amir&mysql_1738",
        database="ALX_prodev"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    # Yield ages one by one
    for row in cursor:
        yield row['age']

    cursor.close()
    conn.close()


def calculate_average_age():
    """
    Consumes the stream_user_ages generator to calculate
    the average user age in a memory-efficient way.
    """
    total_age = 0
    count = 0

    # Single loop — iterate through the generator
    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        print("Average age of users: 0")
    else:
        average_age = total_age / count
        print(f"Average age of users: {average_age:.2f}")


if __name__ == "__main__":
    calculate_average_age()
