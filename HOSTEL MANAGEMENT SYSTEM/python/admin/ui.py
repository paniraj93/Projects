import streamlit as st
import mysql.connector
from datetime import datetime
import re

def validate_name(ename):
    if re.match("^[a-zA-Z ]+$", ename):
        return ename.strip().title()
    else:
        st.warning("Event Name should contain only letters and spaces.")
        return None
    
def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return email
    else:
        st.warning("Please enter a valid email address.")
        return None

def create_connection():
    # Connect to MySQL database
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="652727533266",
        database="hostel_db"
    )
    return mydb

def show_students():
    mydb = create_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT SID, SNAME, EMAIL, REG_DATE, ROOM_NO, CONTACT_INFO, DID FROM STUDENT")
    results = mycursor.fetchall()

    if results:
        st.write("Students:")
        df = pd.DataFrame(results, columns=["SID", "Name", "Email", "Registered Date", "Room No", "Phone No", "Department ID"])
        st.write(df)
    else:
        st.write("No students found.")

import streamlit as st
import mysql.connector
import pandas as pd

def show_logs():
    mydb = create_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM ADMINLOG")
    results = mycursor.fetchall()

    if results:
        st.write("Logs:")
        df = pd.DataFrame(results, columns=["  Log ID  ", "  Admin ID  ", "  Login Time  "])
        st.write(df)
    else:
        st.write("No logs found.")


def show_rooms():
    mydb = create_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM ROOMS")
    results = mycursor.fetchall()

    if results:
        st.write("Rooms:")
        df = pd.DataFrame(results, columns=["Room Number", "    Fees    ", "  Seater  "])
        st.write(df)
    else:
        st.write("No rooms found.")

def add_room():
    st.title("Add Room")

    room_no = st.text_input("Room Number")
    fees = st.text_input("Room Fees")
    seater = st.text_input("Seater Capacity")

    if st.button("Add Room"):
        if not room_no.isdigit() or not fees.isdigit() or not seater.isdigit():
            st.warning("Room number, fees, and seater capacity should be numbers only.")
        else:
            mydb = create_connection()
            mycursor = mydb.cursor()

            query = "INSERT INTO ROOMS (ROOM_NO, FEES, SEATER) VALUES (%s, %s, %s)"
            values = (room_no, fees, seater)
            mycursor.execute(query, values)
            mydb.commit()

            st.success("Room added successfully.")

def register_student():
    st.title("Register Student")

    sid = st.text_input("Student ID")
    sname = st.text_input("Student Name")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    room_no = st.selectbox("Room Number", [""])
    contact_info = st.text_input("Contact Info")
    did = st.selectbox("Department ID", [""])

    if st.button("Register Student"):
        if not sid.startswith("3BR21CS") or len(sid) != 10 or not sid[8:].isdigit():
            st.warning("Student ID should be in format 3BR21CS001")
        elif not sname.replace(" ", "").isalpha():
            st.warning("Student name should contain only letters and spaces")
        elif not "@" in email or not "." in email:
            st.warning("Invalid email address")
        elif not password.startswith("CS") or len(password) != 5 or not password[2:].isdigit():
            st.warning("Password should be in format CS001")
        elif not contact_info.isdigit() or len(contact_info) != 10:
            st.warning("Contact info should be a 10-digit number")
        else:
            mydb = create_connection()
            mycursor = mydb.cursor()

            reg_date = datetime.now().date().isoformat()

            query = "INSERT INTO STUDENT (SID, SNAME, EMAIL, PASSWORD, REG_DATE, ROOM_NO, CONTACT_INFO, DID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (sid, sname, email, password, reg_date, room_no, contact_info, did)
            mycursor.execute(query, values)
            mydb.commit()

            st.success("Student registered successfully.")

def remove_student():
    st.title("Remove Student")

    sid = st.text_input("Enter Student ID:")
    if st.button("Remove Student"):
        mydb = create_connection()
        mycursor = mydb.cursor()

        query = "DELETE FROM STUDENT WHERE SID = %s"
        mycursor.execute(query, (sid,))
        mydb.commit()

        if mycursor.rowcount > 0:
            st.success("Student removed successfully.")
        else:
            st.warning("Student not found.")

def main():
    st.sidebar.title("Event Management System")
    page = st.sidebar.selectbox(
        "Select an option",
        ["Show Students", "Show Logs", "Show Rooms", "Add Room", "Register Student", "Remove Student"]
    )

    if page == "Show Students":
        show_students()
    elif page == "Show Logs":
        show_logs()
    elif page == "Show Rooms":
        show_rooms()
    elif page == "Add Room":
        add_room()
    elif page == "Register Student":
        register_student()
    elif page == "Remove Student":
        remove_student()

if __name__ == "__main__":
    main()
