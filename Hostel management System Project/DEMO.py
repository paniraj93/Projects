import streamlit as st
import mysql.connector

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="652727533266",
    database="hostel_db"
)
mycursor = mydb.cursor()

# Function to validate admin login
def validate_admin(username, password):
    query = "SELECT * FROM ADMIN WHERE USERNAME=%s AND PASSWORD=%s"
    mycursor.execute(query, (username, password))
    result = mycursor.fetchone()
    return result

# Function to validate student login
def validate_student(username, password):
    query = "SELECT * FROM STUDENT WHERE EMAIL=%s AND PASSWORD=%s"
    mycursor.execute(query, (username, password))
    result = mycursor.fetchone()
    return result

# Streamlit app
def main():
    st.title("Hostel Management System")
    st.subheader("Login")

    username = st.text_input("Username/Email:")
    password = st.text_input("Password:", type="password")

    if st.button("Admin Login"):
        admin_result = validate_admin(username, password)
        if admin_result:
            st.success("Admin login successful!")
            # Proceed with admin functionality
        else:
            st.error("Invalid credentials. Please try again.")

    if st.button("Student Login"):
        student_result = validate_student(username, password)
        if student_result:
            st.success("Student login successful!")
            # Proceed with student functionality
        else:
            st.error("Invalid credentials. Please try again.")

if __name__ == "__main__":
    main()
