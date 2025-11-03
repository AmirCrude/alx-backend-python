### **Project: Getting Started with Python Generators**

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

### **Author**

**Amir Abdu**ALX ProDev Backend — _Python Generators Project_
