import wx
import mysql.connector

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="652727533266",
    database="hostel_db"
)
mycursor = mydb.cursor()

# Function to retrieve student details
def get_student_details(sid):
    query = "SELECT * FROM STUDENT WHERE SID=%s"
    mycursor.execute(query, (sid,))
    result = mycursor.fetchone()
    return result

# Function to retrieve department name
def get_department_name(did):
    query = "SELECT CNAME FROM DEPT WHERE DID=%s"
    mycursor.execute(query, (did,))
    result = mycursor.fetchone()
    return result[0] if result else None

class MyFrame(wx.Frame):
    def __init__(self, parent=None, title="WELCOME STUDENT"):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 300))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # StaticText to display student details
        self.student_info_text = wx.StaticText(panel, label="")
        vbox.Add(self.student_info_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # TextCtrl to input SID
        self.sid_textctrl = wx.TextCtrl(panel)
        vbox.Add(self.sid_textctrl, 0, wx.EXPAND | wx.ALL, 5)

        # Button to retrieve student details
        self.retrieve_button = wx.Button(panel, label="Retrieve Student Details")
        self.retrieve_button.Bind(wx.EVT_BUTTON, self.on_retrieve)
        vbox.Add(self.retrieve_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

class MyFrame(wx.Frame):
    def __init__(self, parent=None, title="Details"):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 300))

        panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # StaticText to display student details
        self.student_info_text = wx.StaticText(panel, label="")
        self.vbox.Add(self.student_info_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # TextCtrl to input SID
        self.sid_textctrl = wx.TextCtrl(panel)
        self.vbox.Add(self.sid_textctrl, 0, wx.EXPAND | wx.ALL, 5)

        # Button to retrieve student details
        self.retrieve_button = wx.Button(panel, label="Retrieve Student Details")
        self.retrieve_button.Bind(wx.EVT_BUTTON, self.on_retrieve)
        self.vbox.Add(self.retrieve_button, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        panel.SetSizer(self.vbox)
        self.Centre()
        self.Show()

    def on_retrieve(self, event):
        sid = str(self.sid_textctrl.GetValue())
        student_details = get_student_details(sid)
        if student_details:
            sid, sname, email, _, reg_date, room_no, contact_info, did = student_details
            dname = get_department_name(did)
            if dname:
                student_info = f"SID: {sid}\nSNAME: {sname}\nEMAIL: {email}\nREG_DATE: {reg_date}\nROOM_NO: {room_no}\nCONTACT_INFO: {contact_info}\nDNAME: {dname}"

                # Create a new text box to display the student information
                student_info_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
                student_info_text.SetValue(student_info)
                student_info_text.SetEditable(False)

                # Add the new text box to the sizer
                self.vbox.Add(student_info_text, 0, wx.EXPAND | wx.ALL, 5)

                # Fit the sizer to update the layout
                self.vbox.Fit(self)

            else:
                self.student_info_text.SetLabel("Department not found")
        else:
            self.student_info_text.SetLabel("Student not found")

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(None, title="Student Details")
    app.MainLoop()
