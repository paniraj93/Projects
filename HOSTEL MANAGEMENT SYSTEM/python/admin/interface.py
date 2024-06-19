import wx
import wx.grid
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

class AdminInterface(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Admin Interface", size=(400, 300))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Show Students button
        show_students_button = wx.Button(panel, label="Show Students")
        show_students_button.Bind(wx.EVT_BUTTON, self.on_show_students)
        sizer.Add(show_students_button, 0, wx.ALL|wx.EXPAND, 5)

        # Show Logs button
        show_logs_button = wx.Button(panel, label="Show Logs")
        show_logs_button.Bind(wx.EVT_BUTTON, self.on_show_logs)
        sizer.Add(show_logs_button, 0, wx.ALL|wx.EXPAND, 5)

        # Show Rooms button
        show_rooms_button = wx.Button(panel, label="Show Rooms")
        show_rooms_button.Bind(wx.EVT_BUTTON, self.on_show_rooms)
        sizer.Add(show_rooms_button, 0, wx.ALL|wx.EXPAND, 5)

        # Add Room button
        add_room_button = wx.Button(panel, label="Add Room")
        add_room_button.Bind(wx.EVT_BUTTON, self.on_add_room)
        sizer.Add(add_room_button, 0, wx.ALL|wx.EXPAND, 5)

        # Register Student button
        register_student_button = wx.Button(panel, label="Register Student")
        register_student_button.Bind(wx.EVT_BUTTON, self.on_register_student)
        sizer.Add(register_student_button, 0, wx.ALL|wx.EXPAND, 5)

        # Remove Student button
        remove_student_button = wx.Button(panel, label="Remove Student")
        remove_student_button.Bind(wx.EVT_BUTTON, self.on_remove_student)
        sizer.Add(remove_student_button, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizer)
        self.Show()

    def on_show_students(self, event):
        query = "SELECT SID, SNAME, EMAIL, REG_DATE, ROOM_NO, CONTACT_INFO, DID FROM STUDENT"
        mycursor.execute(query)
        results = mycursor.fetchall()

        if results:
            columns = ["SID", "Name", "Email", "Registered Date", "Room No", "Phone No", "DID"]
            table_data = [[str(result[i]) for i in range(len(result))] for result in results]
            self.show_table_dialog("Students", columns, table_data)
        else:
            wx.MessageBox("No students found.")

    def on_show_logs(self, event):
        query = "SELECT * FROM ADMINLOG"
        mycursor.execute(query)
        results = mycursor.fetchall()

        if results:
            columns = ["Log ID", "Admin ID", "Login Time"]
            table_data = [[str(result[i]) for i in range(len(result))] for result in results]
            self.show_table_dialog("Logs", columns, table_data)
        else:
            wx.MessageBox("No logs found.")

    def on_show_rooms(self, event):
        query = "SELECT * FROM ROOMS"
        mycursor.execute(query)
        results = mycursor.fetchall()

        if results:
            columns = ["Room No", "Fees", "Seater"]
            table_data = [[str(result[i]) for i in range(len(result))] for result in results]
            self.show_table_dialog("Rooms", columns, table_data)
        else:
            wx.MessageBox("No rooms found.")

    def show_table_dialog(self, title, columns, data):
        dialog = wx.Dialog(self, title=title, size=(800, 600))
        panel = wx.Panel(dialog)
        grid = wx.grid.Grid(panel)
        grid.CreateGrid(len(data), len(columns))

        for i, col_name in enumerate(columns):
            grid.SetColLabelValue(i, col_name)

        for i, row in enumerate(data):
            for j, value in enumerate(row):
                grid.SetCellValue(i, j, value)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        dialog.Center()
        dialog.ShowModal()
        dialog.Destroy()



    def on_add_room(self, event):
        dialog = wx.Dialog(None, title="Add Room")
        panel = wx.Panel(dialog)

        sizer = wx.BoxSizer(wx.VERTICAL)

        room_no_label = wx.StaticText(panel, label="Room Number:")
        room_no_text = wx.TextCtrl(panel)
        sizer.Add(room_no_label, 0, wx.ALL, 5)
        sizer.Add(room_no_text, 0, wx.EXPAND|wx.ALL, 5)

        fees_label = wx.StaticText(panel, label="Room Fees:")
        fees_text = wx.TextCtrl(panel)
        sizer.Add(fees_label, 0, wx.ALL, 5)
        sizer.Add(fees_text, 0, wx.EXPAND|wx.ALL, 5)

        seater_label = wx.StaticText(panel, label="Seater Capacity:")
        seater_text = wx.TextCtrl(panel)
        sizer.Add(seater_label, 0, wx.ALL, 5)
        sizer.Add(seater_text, 0, wx.EXPAND|wx.ALL, 5)

        button_sizer = wx.StdDialogButtonSizer()
        button_ok = wx.Button(panel, wx.ID_OK)
        button_cancel = wx.Button(panel, wx.ID_CANCEL)
        button_sizer.AddButton(button_ok)
        button_sizer.AddButton(button_cancel)
        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        panel.SetSizer(sizer)

        if dialog.ShowModal() == wx.ID_OK:
            room_no = room_no_text.GetValue()
            fees = fees_text.GetValue()
            seater = seater_text.GetValue()
            
            def is_number(value):
                try:
                    int(value)
                    return True
                except ValueError:
                    return False

            if not is_number(room_no) or not is_number(fees) or not is_number(seater):
                wx.MessageBox("Room number, fees, and seater capacity should be numbers only.")
                return

            query = "INSERT INTO ROOMS (ROOM_NO, FEES, SEATER) VALUES (%s, %s, %s)"
            values = (room_no, fees, seater)
            mycursor.execute(query, values)
            mydb.commit()

            wx.MessageBox("Room added successfully.")

        dialog.Destroy()

    def on_register_student(self, event):
        dialog = wx.Dialog(None, title="Register Student")
        panel = wx.Panel(dialog)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sid_label = wx.StaticText(panel, label="Student ID:")
        sid_text = wx.TextCtrl(panel)
        sizer.Add(sid_label, 0, wx.ALL, 5)
        sizer.Add(sid_text, 0, wx.EXPAND|wx.ALL, 5)

        sname_label = wx.StaticText(panel, label="Student Name:")
        sname_text = wx.TextCtrl(panel)
        sizer.Add(sname_label, 0, wx.ALL, 5)
        sizer.Add(sname_text, 0, wx.EXPAND|wx.ALL, 5)

        email_label = wx.StaticText(panel, label="Email Address:")
        email_text = wx.TextCtrl(panel)
        sizer.Add(email_label, 0, wx.ALL, 5)
        sizer.Add(email_text, 0, wx.EXPAND|wx.ALL, 5)

        password_label = wx.StaticText(panel, label="Password:")
        password_text = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(password_label, 0, wx.ALL, 5)
        sizer.Add(password_text, 0, wx.EXPAND|wx.ALL, 5)

        reg_date = datetime.datetime.now().date().isoformat()

        room_no_label = wx.StaticText(panel, label="Room Number:")
        room_no_choice = wx.Choice(panel, choices=[""])
        # Populate room numbers from database
        mycursor.execute("SELECT ROOM_NO FROM ROOMS")
        rooms = mycursor.fetchall()
        room_no_choice.SetItems([str(room[0]) for room in rooms])
        sizer.Add(room_no_label, 0, wx.ALL, 5)
        sizer.Add(room_no_choice, 0, wx.EXPAND|wx.ALL, 5)

        contact_info_label = wx.StaticText(panel, label="Contact Info:")
        contact_info_text = wx.TextCtrl(panel)
        sizer.Add(contact_info_label, 0, wx.ALL, 5)
        sizer.Add(contact_info_text, 0, wx.EXPAND|wx.ALL, 5)

        did_label = wx.StaticText(panel, label="Department ID:")
        did_choice = wx.Choice(panel, choices=[""])
        # Populate department IDs and names from database
        mycursor.execute("SELECT DID, CNAME FROM DEPT")
        depts = mycursor.fetchall()
        did_choice.SetItems([f"{dept[1]}: {dept[0]}" for dept in depts])
        sizer.Add(did_label, 0, wx.ALL, 5)
        sizer.Add(did_choice, 0, wx.EXPAND|wx.ALL, 5)

        button_sizer = wx.StdDialogButtonSizer()
        button_ok = wx.Button(panel, wx.ID_OK)
        button_cancel = wx.Button(panel, wx.ID_CANCEL)
        button_sizer.AddButton(button_ok)
        button_sizer.AddButton(button_cancel)
        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        panel.SetSizer(sizer)

        if dialog.ShowModal() == wx.ID_OK:
            sid = sid_text.GetValue()
            sname = sname_text.GetValue()
            email = email_text.GetValue()
            password = password_text.GetValue()
            room_no = room_no_choice.GetStringSelection()
            contact_info = contact_info_text.GetValue()
            did = did_choice.GetStringSelection()

            if not sid.startswith("3BR21CS") or len(sid) != 10 or not sid[8:].isdigit():
                wx.MessageBox("Student ID should be in format 3BR21CS001")
                return
            if not sname.replace(" ", "").isalpha():
                wx.MessageBox("Student name should contain only letters and spaces")
                return
            if not "@" in email or not "." in email:
                wx.MessageBox("Invalid email address")
                return
            if not password.startswith("CS") or len(password) != 5 or not password[2:].isdigit():
                wx.MessageBox("Password should be in format CS001")
                return
            if not contact_info.isdigit() or len(contact_info) != 10:
                wx.MessageBox("Contact info should be a 10-digit number")
                return

            query = "INSERT INTO STUDENT (SID, SNAME, EMAIL, PASSWORD, REG_DATE, ROOM_NO, CONTACT_INFO, DID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (sid, sname, email, password, reg_date, room_no, contact_info, did)
            mycursor.execute(query, values)
            mydb.commit()

            wx.MessageBox("Student registered successfully.")

        dialog.Destroy()


    def on_remove_student(self, event):
        sid = wx.GetTextFromUser("Enter Student ID:", "Remove Student", "Student ID")
        query = "DELETE FROM STUDENT WHERE SID = %s"
        mycursor.execute(query, (sid,))
        mydb.commit()

        if mycursor.rowcount > 0:
            wx.MessageBox("Student removed successfully.")
        else:
            wx.MessageBox("Student not found.")

if __name__ == "__main__":
    app = wx.App()
    frame = AdminInterface()
    app.MainLoop()
