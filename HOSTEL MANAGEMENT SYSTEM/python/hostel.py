# streamlit run hostel.py
import streamlit as st
from admin import ui
import datetime
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
def login():
    st.title("Admin Login")
    admin_id = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        query = "SELECT * FROM ADMIN WHERE USERNAME=%s AND PASSWORD=%s"
        mycursor.execute(query, (admin_id, password))
        result = mycursor.fetchone()

        if result:
            st.success("Login successful!")
            login_time = datetime.datetime.now()

            # Insert login time into the ADMINLOG table
            query = "INSERT INTO ADMINLOG (AID, LOGIN_TIME) VALUES (%s, %s)"
            values = (result[0], login_time)
            mycursor.execute(query, values)
            mydb.commit()
            st.write("Redirecting to event home screen...")
            st.session_state.logged_in = True
            st.rerun()  # Rerun the app to start on a fresh page
        else:
            st.error("Invalid credentials")

# Main Streamlit app
def main():
    if not hasattr(st.session_state, 'logged_in'):
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        st.title("Hostel Home Screen")
        st.write("Welcome to the hostel home screen!")
        ui.main()

if __name__ == "__main__":
    main()
