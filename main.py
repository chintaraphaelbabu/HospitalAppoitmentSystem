from PIL import Image
import numpy as np
import wx.adv as adv
from datetime import datetime, time as dtime
import wx

USERS_FILE = "users.txt"
APPTS_FILE = "appointments.txt"

# --- Modern Panel for consistent style ---
class ModernPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundColour(wx.Colour(245, 248, 255))

    def add_title(self, sizer, text):
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        # Try to load and show a Pillow image as an icon (if exists)
        icon_path = "hospital_icon.png"
        try:
            img = Image.open(icon_path).resize((32, 32))
            img.save("_icon_temp.png")
            bmp = wx.Bitmap("_icon_temp.png", wx.BITMAP_TYPE_PNG)
            hbox.Add(wx.StaticBitmap(self, bitmap=bmp), flag=wx.RIGHT, border=8)
        except Exception:
            pass
        title = wx.StaticText(self, label=text)
        font = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(wx.Colour(30, 60, 120))
        hbox.Add(title, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hbox, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=15)

    def add_label(self, sizer, text):
        label = wx.StaticText(self, label=text)
        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label.SetFont(font)
        label.SetForegroundColour(wx.Colour(60, 60, 60))
        sizer.Add(label, flag=wx.LEFT|wx.TOP, border=8)


# --- Appointment Data ---
SLOTS = {
    "2025-12-05": ["10:00", "10:30", "11:00"],
    "2025-12-06": ["09:00", "09:30", "10:00"]
}

def read_appointments():
    appts = []
    try:
        with open(APPTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 5:
                    appts.append(parts)
    except FileNotFoundError:
        pass
    # Use numpy array for demonstration (not strictly needed, but per requirements)
    if appts:
        return np.array(appts, dtype=object).tolist()
    return appts

def write_appointments(appts):
    try:
        with open(APPTS_FILE, "w", encoding="utf-8") as f:
            for a in appts:
                f.write(",".join(a) + "\n")
    except Exception:
        pass

def load_doctors():
    doctors = []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                # Format: role,username,password[,specialization]
                if len(parts) >= 3 and parts[0] == "doctor":
                    spec = parts[3] if len(parts) >= 4 else "General"
                    doctors.append((parts[1], spec))
    except FileNotFoundError:
        pass
    return doctors

class PatientFrame(wx.Frame):
    def __init__(self, username, login_frame=None):
        super().__init__(None, title=f"Patient: {username}", size=(500, 500))
        self.username = username
        self.login_frame = login_frame
        panel = ModernPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.add_title(vbox, f"Welcome, {username}")
        self.Maximize(True)

        grid = wx.FlexGridSizer(3, 2, 10, 10)
        panel.add_label(grid, "Select Date:")
        self.date_picker = adv.DatePickerCtrl(panel, style=adv.DP_DEFAULT|adv.DP_SHOWCENTURY)
        grid.Add(self.date_picker, flag=wx.EXPAND)

        panel.add_label(grid, "Available Times:")
        self.time_choice = wx.Choice(panel)
        grid.Add(self.time_choice, flag=wx.EXPAND)

        panel.add_label(grid, "Choose Doctor:")
        doc_list = [f"{u} ({s})" for u, s in load_doctors()] or ["dr_smith (General)"]
        self.doctor_choice = wx.Choice(panel, choices=doc_list)
        if doc_list:
            self.doctor_choice.SetSelection(0)
        grid.Add(self.doctor_choice, flag=wx.EXPAND)
        grid.AddGrowableCol(1, 1)
        vbox.Add(grid, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=30)

        # initialize time list for today's date
        self.update_times_for_selected_date()
        self.date_picker.Bind(adv.EVT_DATE_CHANGED, self.on_date_changed)
        self.doctor_choice.Bind(wx.EVT_CHOICE, self.on_doctor_changed)

        book_btn = wx.Button(panel, label="Book Appointment")
        book_btn.SetBackgroundColour(wx.Colour(30, 180, 120))
        book_btn.SetForegroundColour(wx.WHITE)
        vbox.Add(book_btn, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=20)

        panel.add_label(vbox, "Your Appointments:")
        self.appt_list = wx.ListBox(panel, size=(300, 200))
        appt_box = wx.StaticBox(panel, label="Appointments")
        appt_sizer = wx.StaticBoxSizer(appt_box, wx.VERTICAL)
        appt_sizer.Add(self.appt_list, flag=wx.EXPAND|wx.ALL, border=10, proportion=1)
        vbox.Add(appt_sizer, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=30, proportion=1)

        cancel_btn = wx.Button(panel, label="Cancel Selected Appointment")
        cancel_btn.SetBackgroundColour(wx.Colour(200, 60, 60))
        cancel_btn.SetForegroundColour(wx.WHITE)
        vbox.Add(cancel_btn, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        logout_btn = wx.Button(panel, label="Logout")
        logout_btn.SetBackgroundColour(wx.Colour(120, 120, 120))
        logout_btn.SetForegroundColour(wx.WHITE)
        vbox.Add(logout_btn, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)

        self.msg = wx.StaticText(panel, label="")
        font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.msg.SetFont(font)
        self.msg.SetForegroundColour(wx.Colour(200, 40, 40))
        vbox.Add(self.msg, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        panel.SetSizer(vbox)
        self.Centre()

        book_btn.Bind(wx.EVT_BUTTON, self.on_book)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        logout_btn.Bind(wx.EVT_BUTTON, self.on_logout)

        self.refresh_appointments()

    def on_book(self, event):
        # get date string yyyy-mm-dd
        dt = self.date_picker.GetValue()
        date = f"{dt.GetYear():04d}-{dt.GetMonth()+1:02d}-{dt.GetDay():02d}"
        time = self.time_choice.GetStringSelection()
        doc_sel = self.doctor_choice.GetStringSelection()
        if not time or not doc_sel:
            self.msg.SetLabel("Select time and doctor.")
            return
        doctor = doc_sel.split()[0]
        appts = read_appointments()
        # Check if already booked
        for a in appts:
            if a[1] == doctor and a[2] == date and a[3] == time and a[4] == "booked":
                self.msg.SetLabel("Slot already booked.")
                return
        appts.append([self.username, doctor, date, time, "booked"])
        write_appointments(appts)
        self.msg.SetLabel("Appointment booked.")
        self.refresh_appointments()

    def on_date_changed(self, event):
        self.update_times_for_selected_date()

    def update_times_for_selected_date(self):
        dt = self.date_picker.GetValue()
        date = f"{dt.GetYear():04d}-{dt.GetMonth()+1:02d}-{dt.GetDay():02d}"
        # Determine base options from slots or generated intervals
        defined = SLOTS.get(date, [])
        if defined:
            options = defined[:]
        else:
            now = datetime.now()
            is_today = (date == now.strftime('%Y-%m-%d'))
            start_hour = now.hour if is_today else 9
            start_min = now.minute if is_today else 0
            quarter = ((start_min // 15) + 1) * 15
            if quarter == 60:
                start_hour += 1
                quarter = 0
            start_min = quarter
            end_hour = 18
            options = []
            h = start_hour
            m = start_min
            while h < end_hour:
                options.append(f"{h:02d}:{m:02d}")
                m += 15
                if m >= 60:
                    m = 0
                    h += 1
        # Remove times already booked for selected doctor on selected date
        doc_sel = self.doctor_choice.GetStringSelection()
        booked_times = set()
        if doc_sel:
            doctor = doc_sel.split()[0]
            for a in read_appointments():
                if a[1] == doctor and a[2] == date and a[4] == "booked":
                    booked_times.add(a[3])
        filtered = [t for t in options if t not in booked_times]
        self.time_choice.Set(filtered)
        if filtered:
            self.time_choice.SetSelection(0)
        else:
            self.time_choice.Set([])

    def on_doctor_changed(self, event):
        self.update_times_for_selected_date()

    def on_logout(self, event):
        if self.login_frame is not None:
            self.login_frame.Show()
        self.Destroy()

    def on_cancel(self, event):
        idx = self.appt_list.GetSelection()
        if idx == wx.NOT_FOUND:
            self.msg.SetLabel("Select an appointment to cancel.")
            return
        appts = read_appointments()
        own_appts = [a for a in appts if a[0] == self.username]
        if idx >= len(own_appts):
            self.msg.SetLabel("Invalid selection.")
            return
        to_cancel = own_appts[idx]
        appts.remove(to_cancel)
        write_appointments(appts)
        self.msg.SetLabel("Appointment cancelled.")
        self.refresh_appointments()

    def refresh_appointments(self):
        appts = read_appointments()
        own_appts = [a for a in appts if a[0] == self.username]
        self.appt_list.Set([f"Dr: {a[1]} {a[2]} {a[3]} Status: {a[4]}" for a in own_appts])

class DoctorFrame(wx.Frame):
    def __init__(self, username, login_frame=None):
        super().__init__(None, title=f"Doctor: {username}", size=(500, 500))
        self.username = username
        self.login_frame = login_frame
        panel = ModernPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.add_title(vbox, f"Welcome, Dr. {username}")
        self.Maximize(True)

        panel.add_label(vbox, "Your Appointments:")
        self.appt_list = wx.ListBox(panel, size=(300, 300))
        appt_box = wx.StaticBox(panel, label="Today's Schedule")
        appt_sizer = wx.StaticBoxSizer(appt_box, wx.VERTICAL)
        appt_sizer.Add(self.appt_list, flag=wx.EXPAND|wx.ALL, border=10, proportion=1)
        vbox.Add(appt_sizer, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=30, proportion=1)

        self.msg = wx.StaticText(panel, label="")
        font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.msg.SetFont(font)
        self.msg.SetForegroundColour(wx.Colour(200, 40, 40))
        vbox.Add(self.msg, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        logout_btn = wx.Button(panel, label="Logout")
        logout_btn.SetBackgroundColour(wx.Colour(120, 120, 120))
        logout_btn.SetForegroundColour(wx.WHITE)
        vbox.Add(logout_btn, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)

        panel.SetSizer(vbox)
        self.Centre()

        self.refresh_appointments()
        logout_btn.Bind(wx.EVT_BUTTON, self.on_logout)

    def refresh_appointments(self):
        appts = read_appointments()
        my_appts = [a for a in appts if a[1] == self.username]
        self.appt_list.Set([f"Patient: {a[0]} {a[2]} {a[3]} Status: {a[4]}" for a in my_appts])

    def on_logout(self, event):
        if self.login_frame is not None:
            self.login_frame.Show()
        self.Destroy()

class LoginFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))
        panel = ModernPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.add_title(vbox, "Hospital Appointment Manager")

        grid = wx.FlexGridSizer(3, 2, 16, 16)
        panel.add_label(grid, "Role:")
        self.role_choice = wx.Choice(panel, choices=["patient", "doctor"])
        grid.Add(self.role_choice, flag=wx.EXPAND)
        panel.add_label(grid, "Username:")
        self.user_text = wx.TextCtrl(panel)
        grid.Add(self.user_text, flag=wx.EXPAND)
        panel.add_label(grid, "Password:")
        self.pass_text = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        grid.Add(self.pass_text, flag=wx.EXPAND)
        grid.AddGrowableCol(1, 1)
        vbox.Add(grid, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=60)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        login_btn = wx.Button(panel, label="Login")
        reg_btn = wx.Button(panel, label="Register")
        login_btn.SetBackgroundColour(wx.Colour(30, 180, 120))
        login_btn.SetForegroundColour(wx.WHITE)
        reg_btn.SetBackgroundColour(wx.Colour(30, 120, 180))
        reg_btn.SetForegroundColour(wx.WHITE)
        hbox.Add(login_btn, flag=wx.RIGHT, border=20)
        hbox.Add(reg_btn)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=30)

        self.msg = wx.StaticText(panel, label="")
        font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.msg.SetFont(font)
        self.msg.SetForegroundColour(wx.Colour(200, 40, 40))
        vbox.Add(self.msg, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        panel.SetSizer(vbox)
        self.Centre()
        self.Maximize(True)

        login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        reg_btn.Bind(wx.EVT_BUTTON, self.on_register)

    def on_login(self, event):
        role = self.role_choice.GetStringSelection()
        username = self.user_text.GetValue()
        password = self.pass_text.GetValue()
        if not role or not username or not password:
            self.msg.SetLabel("All fields required.")
            return
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    # Accept optional specialization for doctor entries
                    if len(parts) >= 3 and parts[0] == role and parts[1] == username and parts[2] == password:
                        self.msg.SetLabel(f"Login successful as {role}!")
                        wx.MessageBox(f"Welcome, {username}!", "Login", wx.OK|wx.ICON_INFORMATION)
                        self.Hide()
                        if role == "patient":
                            pf = PatientFrame(username, login_frame=self)
                            pf.Show()
                        else:
                            df = DoctorFrame(username, login_frame=self)
                            df.Show()
                        return
        except FileNotFoundError:
            self.msg.SetLabel("No users file. Please register.")
            return
        self.msg.SetLabel("Login failed.")

    def on_register(self, event):
        dlg = RegisterFrame(self)
        dlg.Show()

class RegisterFrame(wx.Frame):
    def __init__(self, login_frame):
        super().__init__(None, title="Register", size=(500, 400))
        self.login_frame = login_frame
        panel = ModernPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel.add_title(vbox, "Create Account")

        grid = wx.FlexGridSizer(4, 2, 12, 12)
        panel.add_label(grid, "Role:")
        self.role_choice = wx.Choice(panel, choices=["patient", "doctor"])
        self.role_choice.SetSelection(0)
        grid.Add(self.role_choice, flag=wx.EXPAND)

        panel.add_label(grid, "Username:")
        self.user_text = wx.TextCtrl(panel)
        grid.Add(self.user_text, flag=wx.EXPAND)

        panel.add_label(grid, "Password:")
        self.pass_text = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        grid.Add(self.pass_text, flag=wx.EXPAND)

        panel.add_label(grid, "Specialization (doctor):")
        self.spec_text = wx.TextCtrl(panel)
        grid.Add(self.spec_text, flag=wx.EXPAND)
        grid.AddGrowableCol(1, 1)
        vbox.Add(grid, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=30)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        submit_btn = wx.Button(panel, label="Register")
        cancel_btn = wx.Button(panel, label="Cancel")
        submit_btn.SetBackgroundColour(wx.Colour(30, 120, 180))
        submit_btn.SetForegroundColour(wx.WHITE)
        hbox.Add(submit_btn, flag=wx.RIGHT, border=10)
        hbox.Add(cancel_btn)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=20)

        self.msg = wx.StaticText(panel, label="")
        vbox.Add(self.msg, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        panel.SetSizer(vbox)
        self.Centre()

        submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_submit(self, event):
        role = self.role_choice.GetStringSelection()
        username = self.user_text.GetValue().strip()
        password = self.pass_text.GetValue().strip()
        specialization = self.spec_text.GetValue().strip() or "General"
        if not role or not username or not password:
            self.msg.SetLabel("All fields required.")
            return
        # append to users file, include specialization for doctors
        line = f"{role},{username},{password}"
        if role == "doctor":
            line += f",{specialization}"
        try:
            with open(USERS_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            self.msg.SetLabel(f"Error saving: {e}")
            return
        wx.MessageBox("Registered successfully. You can login now.", "Register", wx.OK|wx.ICON_INFORMATION)
        self.login_frame.msg.SetLabel("Registered. Please login.")
        self.Destroy()

    def on_cancel(self, event):
        self.Destroy()

class HospitalApp(wx.App):
    def OnInit(self):
        self.frame = LoginFrame(None, title="Hospital Appointment Manager")
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = HospitalApp()
    app.MainLoop()


