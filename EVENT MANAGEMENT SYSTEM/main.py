import streamlit as st
import mysql.connector
from event_management_system import event_management_app
#streamlit run e:/manishma/main.py

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="652727533266",
    database="events"
)
mycursor = mydb.cursor()

# Streamlit login page
def login():
    st.title("Admin Login")
    admin_id = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        mycursor.execute("SELECT * FROM ADMIN WHERE ADMIN_ID = %s AND PASSWORD = %s", (admin_id, password))
        result = mycursor.fetchone()

        if result:
            st.success("Login successful!")
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
        st.write("Welcome to the event home screen!")
        event_management_app.main()

if __name__ == "__main__":
    main()
