import tkinter as tk
from tkinter import ttk
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine

# Function to connect to the MySQL database
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="652727533266",  # Replace with your MySQL password
            database="HOSTEL_DB"
        )
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to MySQL database:", e)
        return None

# Function to execute SQL queries
def execute_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    except mysql.connector.Error as e:
        print("Error executing query:", e)
        return None

# Function to fetch data from MySQL database into a Pandas DataFrame
def fetch_data(conn, query):
    try:
        engine = create_engine('mysql+mysqlconnector://root:652727533266@localhost:3306/HOSTEL_DB')
        data = pd.read_sql(query, engine)
        return data
    except Exception as e:
        print("Error fetching data:", e)
        return None

# Function to handle admin login
def admin_login(username, password, root, login_frame):
    conn = connect_to_db()
    if conn:
        query = f"SELECT * FROM admin WHERE username = '{username}' AND password = '{password}';"
        data = fetch_data(conn, query)
        if data.shape[0] > 0:
            # Set up the main application window after successful login
            main_application(root, conn)
            login_frame.grid_forget()
        else:
            print("Invalid credentials")

# Function to handle adding a new student
def add_student(conn, first_name, last_name, gender, contact_no, email, guardian_name, guardian_relation, guardian_contact_no, payment_address, payment_city, payment_state, payment_pincode):
    if conn:
        query = """
            INSERT INTO registration 
            (firstName, lastName, gender, contactno, emailid, guardianName, guardianRelation, guardianContactno, pmntAddress, pmntCity, pmnatetState, pmntPincode) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (first_name, last_name, gender, contact_no, email, guardian_name, guardian_relation, guardian_contact_no, payment_address, payment_city, payment_state, payment_pincode)
        cursor = execute_query(conn, query, params)
        if cursor:
            print("Student added successfully")
        else:
            print("Error adding student")
# Function to handle removing a student
def remove_student(student_id):
    conn = connect_to_db()
    if conn:
        query = f"DELETE FROM registration WHERE id = {student_id};"
        cursor = execute_query(conn, query)
        if cursor:
            print("Student removed successfully")
        else:
            print("Error removing student")

# Function to handle updating student details
def update_student(student_id, data):
    conn = connect_to_db()
    if conn:
        query = "UPDATE registration SET firstName = %s, middleName = %s, lastName = %s, gender = %s, contactno = %s, emailid = %s WHERE id = %s;"
        cursor = execute_query(conn, query, (data["firstName"], data["middleName"], data["lastName"], data["gender"], data["contactno"], data["emailid"], student_id))
        if cursor:
            print("Student updated successfully")
        else:
            print("Error updating student")

# Function to handle viewing all students
def view_students():
    conn = connect_to_db()
    if conn:
        query = "SELECT * FROM registration;"
        data = fetch_data(conn, query)
        print(data)

# Main application window
def main_application(root, conn):
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, padx=20, pady=20)

    ttk.Label(main_frame, text="Welcome to Hostel Management System", font=("Helvetica", 16)).grid(row=0, column=0, padx=10, pady=10)

    # Add buttons for different functionalities
    ttk.Button(main_frame, text="Add Student", command=lambda: add_student_window(root, conn)).grid(row=1, column=0, padx=5, pady=5)
    ttk.Button(main_frame, text="View Students", command=view_students).grid(row=2, column=0, padx=5, pady=5)
    ttk.Button(main_frame, text="Exit", command=root.destroy).grid(row=3, column=0, padx=5, pady=5)

# Function to open window for adding a new student
def add_student_window(root, conn):
    add_student_window = tk.Toplevel(root)
    add_student_window.title("Add Student")

    # Labels and Entry fields for student details
    ttk.Label(add_student_window, text="First Name:").grid(row=0, column=0, padx=5, pady=5)
    first_name_entry = ttk.Entry(add_student_window)
    first_name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Last Name:").grid(row=1, column=0, padx=5, pady=5)
    last_name_entry = ttk.Entry(add_student_window)
    last_name_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Gender:").grid(row=2, column=0, padx=5, pady=5)
    gender_entry = ttk.Combobox(add_student_window, values=["Male", "Female"])
    gender_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Contact No:").grid(row=3, column=0, padx=5, pady=5)
    contact_no_entry = ttk.Entry(add_student_window)
    contact_no_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Email ID:").grid(row=4, column=0, padx=5, pady=5)
    email_entry = ttk.Entry(add_student_window)
    email_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Guardian Name:").grid(row=5, column=0, padx=5, pady=5)
    guardian_name_entry = ttk.Entry(add_student_window)
    guardian_name_entry.grid(row=5, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Guardian Relation:").grid(row=6, column=0, padx=5, pady=5)
    guardian_relation_entry = ttk.Entry(add_student_window)
    guardian_relation_entry.grid(row=6, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Guardian Contact No:").grid(row=7, column=0, padx=5, pady=5)
    guardian_contact_no_entry = ttk.Entry(add_student_window)
    guardian_contact_no_entry.grid(row=7, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Payment Address:").grid(row=8, column=0, padx=5, pady=5)
    payment_address_entry = ttk.Entry(add_student_window)
    payment_address_entry.grid(row=8, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Payment City:").grid(row=9, column=0, padx=5, pady=5)
    payment_city_entry = ttk.Entry(add_student_window)
    payment_city_entry.grid(row=9, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Payment State:").grid(row=10, column=0, padx=5, pady=5)
    payment_state_entry = ttk.Entry(add_student_window)
    payment_state_entry.grid(row=10, column=1, padx=5, pady=5)

    ttk.Label(add_student_window, text="Payment Pincode:").grid(row=11, column=0, padx=5, pady=5)
    payment_pincode_entry = ttk.Entry(add_student_window)
    payment_pincode_entry.grid(row=11, column=1, padx=5, pady=5)

    ttk.Button(add_student_window, text="Save", command=lambda: add_student(
        conn, 
        first_name_entry.get(), 
        last_name_entry.get(), 
        gender_entry.get(), 
        contact_no_entry.get(), 
        email_entry.get(),
        guardian_name_entry.get(),
        guardian_relation_entry.get(),
        guardian_contact_no_entry.get(),
        payment_address_entry.get(),
        payment_city_entry.get(),
        payment_state_entry.get(),
        payment_pincode_entry.get()
    )).grid(row=12, column=0, columnspan=2, padx=5, pady=5)

    # Add your main application code here
    pass

# Main function to create the GUI
def main():
    conn = connect_to_db()  # Connect to the MySQL database

    # GUI setup
    root = tk.Tk()
    root.title("Hostel Management System")

    # Login Frame
    login_frame = ttk.Frame(root)
    login_frame.grid(row=0, column=0, padx=20, pady=20)

    ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
    username_entry = ttk.Entry(login_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(login_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    login_button = ttk.Button(login_frame, text="Login", command=lambda: admin_login(username_entry.get(), password_entry.get(), root, login_frame))
    login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    # Add more frames, widgets, and event bindings for other functionalities

    root.mainloop()

if __name__ == "__main__":
    main()
