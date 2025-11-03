#!/usr/bin/python3
import mysql.connector
from mysql.connector import errorcode
import csv
import uuid

# 1️⃣ Connect to MySQL server
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Amir&mysql_1738"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# 2️⃣ Create database if it doesn’t exist
def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        print("Database ALX_prodev created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")


# 3️⃣ Connect to ALX_prodev database
def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Amir&mysql_1738",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev: {err}")
        return None


# 4️⃣ Create table user_data if not exists
def create_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL
            );
        """)
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")


# 5️⃣ Insert CSV data
def insert_data(connection, csv_file):
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = row['age']
                cursor.execute("""
                    INSERT IGNORE INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, age))
        connection.commit()
        print("Data inserted successfully")
        cursor.close()
    except Exception as e:
        print(f"Error inserting data: {e}")
