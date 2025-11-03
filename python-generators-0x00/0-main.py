#!/usr/bin/python3

import seed

def main():
    # Step 1: connect to MySQL server (not to any specific database yet)
    connection = seed.connect_db()
    if connection:
        seed.create_database(connection)
        connection.close()
        print("Connection successful")

        # Step 2: connect to the newly created database
        connection = seed.connect_to_prodev()

        if connection:
            # Step 3: create table if not exists
            seed.create_table(connection)

            # Step 4: insert data from CSV
            seed.insert_data(connection, 'user_data.csv')

            # Step 5: confirm database and print 5 sample rows
            cursor = connection.cursor()
            cursor.execute(
                "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';"
            )
            result = cursor.fetchone()
            if result:
                print("Database ALX_prodev is present")

            cursor.execute("SELECT * FROM user_data LIMIT 5;")
            rows = cursor.fetchall()
            print(rows)
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
