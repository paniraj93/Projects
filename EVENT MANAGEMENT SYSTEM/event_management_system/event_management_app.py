import streamlit as st
import mysql.connector
from datetime import datetime
import re

def validate_name(ename):
    if re.match("^[a-zA-Z ]+$", ename):
        return ename.strip().title()
    else:
        st.warning("This field should contain only letters and spaces.")
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
        database="events"
    )
    return mydb

def add_event():
    st.title("Add Event")
    mydb = create_connection()
    mycursor = mydb.cursor()
    eid = st.number_input("Event ID", min_value=0)
    ename = st.text_input("Event Name", value="")
    ename = validate_name(ename)
    edate = st.date_input("Event Date", min_value=datetime.today())
    mycursor.execute("SELECT VID, VNAME FROM VENUE")
    venues = mycursor.fetchall()
    venue_options = [f"{venue[0]}: {venue[1]}" for venue in venues]
    # Display the selectbox
    selected_venue = st.selectbox("Venue ID", venue_options)
    vid = int(selected_venue.split(":")[0])  # Extract the integer part from the select box value

    if st.button("Add Event"):
        # Insert event into database
        try:
            mycursor.execute("INSERT INTO EVENT (EID, ENAME, EDATE, VID) VALUES (%s, %s, %s, %s)", (eid, ename, edate, vid))
            mydb.commit()
            st.success("Event added successfully")
        except mysql.connector.Error as e:
            st.error(f"Error adding event: {e}")
        finally:
            mycursor.close()
            mydb.close()

def show_events():
    st.title("Show Events")

    # Connect to MySQL and retrieve events
    mydb = create_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM EVENT")
    events = mycursor.fetchall()

    # Display events in a table
    if events:
        st.write("Events:")
        event_data = [["Event ID", "Event Name", "Event Date", "Venue ID"]]
        event_data.extend(events)
        st.table(event_data)
    else:
        st.write("No events found")



    mycursor.close()
    mydb.close()

def add_venue():
    st.title("Add Venue")

    vid = st.number_input("Venue ID", min_value=0)
    vname = st.text_input("Venue Name", value="")
    vname = validate_name(vname)
    capacity = st.number_input("Capacity", min_value=0)
    location = st.text_input("Location", value="")
    location = validate_name(location)

    if st.button("Add Venue"):
        mydb = create_connection()
        mycursor = mydb.cursor()

        # Insert venue into database
        try:
            mycursor.execute("INSERT INTO VENUE (VID, VNAME, CAPACITY, LOCATION) VALUES (%s, %s, %s, %s)", (vid, vname, capacity, location))
            mydb.commit()
            st.success("Venue added successfully")
        except mysql.connector.Error as e:
            st.error(f"Error adding venue: {e}")
        finally:
            mycursor.close()
            mydb.close()

def show_venues():
    st.title("Show Venues")

    # Connect to MySQL and retrieve venues
    mydb = create_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM VENUE")
    venues = mycursor.fetchall()

    # Display venues in a table
    if venues:
        st.write("Venues:")
        venue_data = [["Venue ID", "Venue Name", "Capacity", "Location"]]
        venue_data.extend(venues)
        st.table(venue_data)
    else:
        st.write("No venues found")


    mycursor.close()
    mydb.close()

def add_attendees():
    st.title("Add Attendees")

    mydb = create_connection()
    mycursor = mydb.cursor()

    # Get list of events
    mycursor.execute("SELECT EID, ENAME FROM EVENT")
    events = mycursor.fetchall()
    event_names = {ename: eid for eid, ename in events}
    selected_event = st.selectbox("Select Event", list(event_names.keys()))

    # Get EID of selected event
    eid = event_names[selected_event]

    name = st.text_input("Name", value="")
    name = validate_name(name)
    email = st.text_input("Email")
    email = validate_email(email)
    address = st.text_input("Address",  value="")

    if st.button("Add Attendee"):
        # Insert attendee into database
        try:
            mycursor.execute("INSERT INTO ATTENDEE (NAME, EMAIL, ADDRESS, EID) VALUES (%s, %s, %s, %s)", (name, email, address, eid))
            mydb.commit()
            st.success("Attendee added successfully")
        except mysql.connector.Error as e:
            st.error(f"Error adding attendee: {e}")
        finally:
            mycursor.close()
            mydb.close()


def show_attendees():
    st.title("Show Attendees")

    mydb = create_connection()
    mycursor = mydb.cursor()

    # Get list of venues
    mycursor.execute("SELECT VID, VNAME FROM VENUE")
    venues = mycursor.fetchall()
    venue_names = {vname: vid for vid, vname in venues}
    selected_venue = st.selectbox("Select Venue", list(venue_names.keys()))

    # Get VID of selected venue
    vid = venue_names[selected_venue]

    # Get list of events for the selected venue
    mycursor.execute("SELECT EID, ENAME FROM EVENT WHERE VID = %s", (vid,))
    events = mycursor.fetchall()
    event_names = {ename: eid for eid, ename in events}
    selected_event = st.selectbox("Select Event", list(event_names.keys()))

    # Get EID of selected event
    eid = event_names[selected_event]

    # Show attendees for selected event
    mycursor.execute("SELECT NAME, EMAIL, ADDRESS FROM ATTENDEE WHERE EID = %s", (eid,))
    attendees = mycursor.fetchall()

    # Display attendees in a table
    if attendees:
        st.write("Attendees:")
        attendee_data = [["Name", "Email", "Address"]]
        attendee_data.extend(attendees)
        st.table(attendee_data)
    else:
        st.write("No attendees found")

    mycursor.close()
    mydb.close()


def main():
    st.sidebar.title("Event Management System")
    page = st.sidebar.selectbox(
        "Select an option",
        ["Add Event", "Show Events", "Add Venue", "Show Venues", "Add Attendees", "Show Attendees"]
    )

    if page == "Add Event":
        add_event()
    elif page == "Show Events":
        show_events()
    elif page == "Add Venue":
        add_venue()
    elif page == "Show Venues":
        show_venues()
    elif page == "Add Attendees":
        add_attendees()
    elif page == "Show Attendees":
        show_attendees()

if __name__ == "__main__":
    main()
