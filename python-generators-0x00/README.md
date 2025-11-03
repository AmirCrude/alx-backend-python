### **Project: Getting Started with Python Generators**

#### Task-0: Python Generators

#### **Objective**

This project introduces the use of **Python generators** to stream data efficiently from an SQL database — one row at a time.You’ll also learn how to:

- Connect to a MySQL database using Python.
- Create databases and tables programmatically.
- Insert and query data from a .csv file.
- Implement efficient data handling using generators.

Project Structurealx-backend-python/

```css
alx-backend-python/
└── python-generators-0x00/
    ├── seed.py
    ├── 0-main.py
    ├── user\_data.csv
    └── README.md
```

### **Files**

#### **seed.py**

Contains all the core functions:

- connect_db(): Connects to the MySQL server.
- create_database(connection): Creates the database **ALX_prodev** if it doesn’t exist.
- connect_to_prodev(): Connects to the **ALX_prodev** database.
- create_table(connection): Creates the **user_data** table if it doesn’t exist.
- insert_data(connection, data): Inserts user data from the user_data.csv file.

#### **0-main.py**

Used to test all the database setup and data insertion functions.

#### **user_data.csv**

Sample dataset containing user information (UUID, name, email, and age).

### 🛠️ **Setup Instructions**

#### 1\. **Install Python (if not installed)**

Download and install Python 3 from [python.org/downloads](https://www.python.org/downloads/). **Make sure to check** “Add Python to PATH” during installation.

Verify installation:

```bash
python --version
pip --version
```

#### 2\. **Install MySQL Connector**

Install the MySQL driver for Python:

```bash
pip install mysql-connector-python
```

#### 3\. **Ensure MySQL is Installed and Running**

If MySQL is not yet installed, download it from:🔗 https://dev.mysql.com/downloads/mysql

Once installed:

- Make sure the MySQL service is **running**.
- Note your MySQL username and password (usually root).

#### 4\. **Run the Project**

1.  Open a terminal in the python-generators-0x00 folder.
2.  Run:

```bash
python 0-main.py
```

Expected Output:

```css
connection successful
Table user_data created successfully
Database ALX_prodev is present
\[('UUID1', 'Name1', 'Email1', 25), ('UUID2', 'Name2', 'Email2', 30), ...\]
```

Example Output:

```css
connection successful
Table user_data created successfully
Database ALX_prodev is present
\[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67),
('006bfede-724d-4cdd-a2a6-59700f40d0da', 'Glenda Wisozk', 'Miriam21@gmail.com', 119),
('006e1f7f-90c2-45ad-8c1d-1275d594cc88', 'Daniel Fahey IV', 'Delia.Lesch11@hotmail.com', 49)\]
```

#### Task-2: Batch processing Large Data

#### **Objective**

This task introduces **_batch processing using Python generators_** to efficiently handle large datasets from a SQL database. Instead of fetching all rows at once, data is fetched in **_batches_**, and users over a specific age (e.g., 25) are filtered.

Project Structure

```css
    python-generators-0x00/
    ├── 1-batch_processing.py
    ├── 2-main.py
    └── README.md
```

### **Files**

#### **1-batch_processing.py**

Contains the generator and processing functions:

1. stream_users_in_batches(batch_size)

   - Connects to the MySQL database.

   - Fetches rows from user_data table in batches of size batch_size.

   - Yields each batch as a list of dictionaries.

2. batch_processing(batch_size)

   - Iterates over each batch.

   - Filters users whose age > 25.

   - Prints each filtered user.

#### **2-main.py**

Used to test the batch processing function:

- batch_size=50 controls how many rows are processed per batch.
- Wrapping in try/except BrokenPipeError ensures piping output to tools like head won’t crash the script.

#### **Run the Project**

```bash
python 2-main.py | head -n 5
python 2-main.py | Select-Object -First 5
```

Expected output (first 5 users over age 25):

```bash
{'user_id': '0018d17b-7b00-4e66-81e8-ec97e58fd8d7', 'name': 'Claudia Anderson V', 'email': 'Esther77@hotmail.com', 'age': Decimal('96')}
{'user_id': '00c36b62-319d-4ee9-8095-48b659e4d835', 'name': 'Jeff Koss', 'email': 'Dora.Mann80@gmail.com', 'age': Decimal('104')}
{'user_id': '00e54721-58fc-45ad-a6db-a501fb03a03f', 'name': 'Jake Wiegand', 'email': 'Ethel_Runolfsdottir83@hotmail.com', 'age': Decimal('57')}
...

```

### **Author**

**Amir Abdu**ALX ProDev Backend — _Python Generators Project_
