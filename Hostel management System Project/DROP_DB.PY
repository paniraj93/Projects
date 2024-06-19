import mysql.connector

def drop_all_tables(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()

        # Get the list of tables in the database
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()

        # Drop each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            print(f"Dropped table: {table_name}")

        print("All tables dropped successfully.")

        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print("Error:", e)

# Provide your MySQL database connection details
host = "localhost"
user = "root"
password = "652727533266"
database = "HOSTEL_DB"

# Call the function to drop all tables
drop_all_tables(host, user, password, database)
