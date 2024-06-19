import wx
from admin import interface
import mysql.connector
import datetime

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="652727533266",
    database="hostel_db"
)
mycursor = mydb.cursor()

class HostelManagementSystem(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Hostel Management System", size=(400, 300))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Username/Email input
        username_label = wx.StaticText(panel, label="Username:")
        self.username_text = wx.TextCtrl(panel)
        sizer.Add(username_label, 0, wx.ALL, 5)
        sizer.Add(self.username_text, 0, wx.EXPAND|wx.ALL, 5)

        # Password input
        password_label = wx.StaticText(panel, label="Password:")
        self.password_text = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(password_label, 0, wx.ALL, 5)
        sizer.Add(self.password_text, 0, wx.EXPAND|wx.ALL, 5)

        # Admin login button
        admin_button = wx.Button(panel, label="Admin Login")
        admin_button.Bind(wx.EVT_BUTTON, self.on_admin_login)
        sizer.Add(admin_button, 0, wx.ALL|wx.ALIGN_CENTER, 5)

        panel.SetSizer(sizer)
        self.Show()

    def on_admin_login(self, event):
        username = self.username_text.GetValue()
        password = self.password_text.GetValue()

        query = "SELECT * FROM ADMIN WHERE USERNAME=%s AND PASSWORD=%s"
        mycursor.execute(query, (username, password))
        result = mycursor.fetchone()

        if result:
            wx.MessageBox("Admin login successful!")
            # Get the current datetime
            login_time = datetime.datetime.now()

            # Insert login time into the ADMINLOG table
            query = "INSERT INTO ADMINLOG (AID, LOGIN_TIME) VALUES (%s, %s)"
            values = (result[0], login_time)
            mycursor.execute(query, values)
            mydb.commit()
            
            interface.AdminInterface()
        else:
            wx.MessageBox("Invalid credentials. Please try again.")

if __name__ == "__main__":
    app = wx.App()
    frame = HostelManagementSystem()
    app.MainLoop()
