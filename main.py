#Created by Cody Willard on 3/21/20.


import tkinter as tkr
import sqlite3
from tkinter import messagebox
from tkinter import ttk
import datetime

database = "passassign.db"
conn = sqlite3.connect(database)
cur = conn.cursor()

root = tkr.Tk()
root.title("Property Check In")
root.resizable(False, False)

def center_window(w=300, h=200):
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry('+%d+%d' % (x, y))


center_window(825, 470)

with conn:
    cur.execute("""CREATE TABLE IF NOT EXISTS assign(
                    pass_num text,
                    name text,
                    badge_num text,
                    description text
                    )""")
    conn.commit()

with conn:
    cur.execute("""CREATE TABLE IF NOT EXISTS scanlog(
                    date text,
                    time text,
                    pass_num text,
                    name text,
                    badge_num text,
                    owner_name text,
                    owner_badge text,
                    description text)
                    """)
    conn.commit()

with conn:
    cur.execute("""CREATE TABLE IF NOT EXISTS checkin(
                    date text,
                    time text,
                    pass_num text,
                    name text,
                    badge_num text,
                    owner_name,
                    owner_badge,
                    description)
                    """)
    conn.commit()


def getdate():
    date = datetime.date.today()
    return date


def gettime():
    time = datetime.datetime.now()
    time_now = time.strftime("%H:%M")
    return time_now


def deleteOld():
    with conn:
        cur.execute("SELECT * FROM scanlog")
        x = cur.fetchall()
        for i in x:
            a = i[0].split("-")
            years = a[0]
            months = a[1]
            days = a[2]
            date = datetime.date(int(years), int(months), int(days))
            if date < (getdate() - datetime.timedelta(days=90)):
                cur.execute("DELETE FROM scanlog WHERE date = ? AND time = ?", (i[0], i[1],))


# ============To create space for UI to look right =============================
class Spacer:
    def __init__(self, row, column):
        self.row = row
        self.column = column

    def label(self):
        space = tkr.Label(root, text="")
        space.grid(row=self.row, column=self.column)


# ============= To assign new properties to pass numbers =============================
class AddToDb:
    def __init__(self, pass_num, first_name, last_name, badge_num, description, connection):
        self.pass_num = pass_num
        self.name = first_name + " " + last_name
        self.badge_num = badge_num
        self.description = description
        self.connection = connection

    def adddata(self):
        with self.connection:
            sql = '''INSERT INTO assign(pass_num, name, badge_num, description)
                        VALUES(?,?,?,?)'''
            assignment = (self.pass_num, self.name, self.badge_num, self.description)
            curs = self.connection.cursor()
            curs.execute(sql, assignment)
            self.connection.commit()


# ================= For adding into the scan log everytime checked in or out ===========================
class AddToScanLog:
    def __init__(self, pass_num, name, badge_num, connection):
        self.date = getdate()
        self.time = gettime()
        self.pass_num = pass_num
        self.name = name
        self.badge_num = badge_num
        self.connection = connection

    def addtolog(self):
        owner_name = []
        owner_badge = []
        description = []
        curs = self.connection.cursor()

        with self.connection:
            getfrom = """SELECT * FROM assign WHERE pass_num = ?"""
            curs.execute(getfrom, (self.pass_num,))
            item = curs.fetchall()
            for value in item:
                owner_name.append(value[1])
                owner_badge.append(value[2])
                description.append(value[3])
            self.connection.commit()

        with self.connection:
            loglist = (self.date, self.time, self.pass_num, self.name, self.badge_num, owner_name[0],
                       owner_badge[0], description[0])
            insert = """INSERT INTO scanlog(date, time, pass_num, name, badge_num,
                    owner_name, owner_badge, description) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
            curs.execute(insert, (loglist))
            self.connection.commit()


# ==================== To get the name if no name is found ====================
class GetName:
    def __init__(self, pass_num, badge_num, root):
        self.pass_num = pass_num
        self.badge_num = badge_num
        self.root = root


    def center_window(self, w, h, top):
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        top.geometry('+%d+%d' % (x, y))

    def new_win(self):
        top = tkr.Toplevel(self.root)
        top.title("Enter Name")
        top.resizable(False, False)
        label = tkr.Label(top, text="Could not find name: Enter name of person checking in or out.")
        label.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        first_name_label = tkr.Label(top, text="Enter first name: ")
        first_name_label.grid(row=2, column=0, padx=5, pady=5)

        first_name_entry = tkr.Entry(top)
        first_name_entry.grid(row=2, column=1, padx=5, pady=5)

        last_name_label = tkr.Label(top, text="Enter last name:")
        last_name_label.grid(row=3, column=0, padx=5, pady=5)

        last_name_entry = tkr.Entry(top)
        last_name_entry.grid(row=3, column=1, padx=5, pady=5)

        ok_button = tkr.Button(top, text="Enter", width=6, height=2, command=lambda: fetchname(self.pass_num,
                                                                            first_name_entry.get().replace(" ", ""),
                                                                            last_name_entry.get().replace(" ", ""),
                                                                            self.badge_num, top))
        ok_button.grid(row=2, column=3, padx=5, pady=5)
        quit_button = tkr.Button(top, text="Exit", width=6, height=2, command=lambda: top.destroy())
        quit_button.grid(row=3, column=3, padx=5, pady=5)
        self.center_window(475, 150, top)


def fetchname(pass_num, first_name, last_name, badge_num, top):
    pass_num = pass_num
    name = first_name + " " + last_name
    badge_num = badge_num
    top = top
    AddToScanLog(pass_num, name, badge_num, conn).addtolog()
    AddToCheckedIn(pass_num, name, badge_num, conn).addcheckin()
    return top.destroy()


# ========== Calls class to add to database scanlog and checkin and deletes from check in if odd number of entries
checkin_name = []


def calladd(event):
    pass_num = scanPassInput.get().replace(" ", "")
    badge_num = scanBadgeInput.get().replace(" ", "")
    badge_assigned = []
    name = []
    pass_entered = []
    pass_entered.clear()
    badge_assigned.clear()
    name.clear()
    checkin_name.clear()

    with conn:
        cur.execute("SELECT * FROM assign WHERE pass_num = ?", (pass_num,))
        m = cur.fetchall()
        pass_entered.append(m)
        conn.commit()
    if pass_num == str("") or badge_num == str(""):
        messagebox.showwarning("Warning", "Entries not fully complete.")
        scanPassInput.focus()

    elif len(pass_entered[0]) < 1:
        messagebox.showwarning("Warning", "Pass scanned does not match any pass assigned.")
        scanPassInput.delete(0, 'end')
        scanBadgeInput.delete(0, 'end')
        scanPassInput.focus()

    else:
        # ========= Gets badge num from assign to compare to scanned badge
        with conn:
            cur.execute("SELECT * FROM assign WHERE pass_num = ?", (pass_num,))
            a = cur.fetchall()
            for i in a:
                badge_assigned.append(i[2])
        conn.commit()

        if badge_num == badge_assigned[0]:
            with conn:
                cur.execute("SELECT * FROM assign WHERE badge_num = ?", (badge_num,))
                a = cur.fetchall()
                for i in a:
                    name.append(i[1])
            conn.commit()
            AddToScanLog(pass_num, name[0], badge_num, conn).addtolog()
            with conn:
                cur.execute("SELECT * FROM scanlog WHERE pass_num = ?", (pass_num,))
                c = cur.fetchall()
                if (len(c) % 2) == 0:
                    with conn:
                        cur.execute("DELETE FROM checkin WHERE pass_num = ?", (pass_num,))
                        addtolistbox()
                        scanPassInput.delete(0, 'end')
                        scanBadgeInput.delete(0, 'end')
                        scanPassInput.focus()
                    conn.commit()
                else:
                    AddToCheckedIn(pass_num, name[0], badge_num, conn).addcheckin()
        else:
            messagebox.showwarning("Warning", "Associate scanned does not match the associate the pass is assigned to.")
            # ============ Looks for name in assign
            if len(checkin_name) == 0:
                with conn:
                    cur.execute("SELECT * FROM assign WHERE badge_num = ?", (badge_num,))
                    d = cur.fetchall()
                    for z in d:
                        checkin_name.append(z[1])
                    conn.commit()

            # ========== looks for name in scanlog
            if len(checkin_name) == 0:
                with conn:
                    cur.execute("SELECT * FROM scanlog WHERE badge_num = ?", (badge_num,))
                    e = cur.fetchall()
                    for y in e:
                        checkin_name.append(y[3])
                    conn.commit()

            # ========== Calls function that creates pop up to get name
            if len(checkin_name) == 0:
                GetName(pass_num, badge_num, root).new_win()
            else:
                AddToScanLog(pass_num, checkin_name[0], badge_num, conn).addtolog()
                with conn:
                    cur.execute("SELECT pass_num FROM scanlog WHERE pass_num = ?", (pass_num,))
                    f = cur.fetchall()
                    if (len(f) % 2) == 0:
                        with conn:
                            cur.execute("DELETE FROM checkin WHERE pass_num = ?", (pass_num,))
                            addtolistbox()
                            scanPassInput.delete(0, 'end')
                            scanBadgeInput.delete(0, 'end')
                            scanPassInput.focus()
                    else:
                        AddToCheckedIn(pass_num, checkin_name[0], badge_num, conn).addcheckin()


# ======= Adds to DB checked in if currently checked in
class AddToCheckedIn:
    def __init__(self, pass_num, name, badge_num, connection):
        self.date = getdate()
        self.time = gettime()
        self.pass_num = pass_num
        self.name = name
        self.badge_num = badge_num
        self.connection = connection

    def addcheckin(self):
        owner_name = []
        owner_badge = []
        description = []
        curs = self.connection.cursor()
        with conn:
            cur.execute("SELECT pass_num FROM scanlog WHERE pass_num = ?", (self.pass_num,))
            f = cur.fetchall()
            if (len(f) % 2) == 0:
                with conn:
                    cur.execute("DELETE FROM checkin WHERE pass_num = ?", (self.pass_num,))
                    addtolistbox()
                    scanPassInput.delete(0, 'end')
                    scanBadgeInput.delete(0, 'end')
                    scanPassInput.focus()
            else:
                with self.connection:
                    getfrom = """SELECT * FROM assign WHERE pass_num = ?"""
                    curs.execute(getfrom, (self.pass_num,))
                    item = curs.fetchall()
                    for value in item:
                        owner_name.append(value[1])
                        owner_badge.append(value[2])
                        description.append(value[3])
                    conn.commit()

                with self.connection:
                    loglist = (self.date, self.time, self.pass_num, self.name, self.badge_num, owner_name[0],
                               owner_badge[0], description[0])
                    insert = """INSERT INTO checkin(date, time, pass_num, name, badge_num,
                            owner_name, owner_badge, description) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"""
                    curs.execute(insert, (loglist))
                    self.connection.commit()

        scanPassInput.delete(0, 'end')
        scanBadgeInput.delete(0, 'end')
        scanPassInput.focus()
        addtolistbox()


# ================== For creating the window to add new users and passes ========================
def adduserwindow():
    top = tkr.Toplevel(root)
    top.title("Add New Property")
    top.resizable(False, False)
    w = 475
    h = 270
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    top.geometry('+%d+%d' % (x, y))
    passnumberlabel = tkr.Label(top, text="Pass number:")
    passnumberlabel.grid(row=0, column=0)

    passnumberinput = tkr.Entry(top)
    passnumberinput.grid(row=0, column=1, padx=10, pady=10)

    firstnamelabel = tkr.Label(top, text="First name:")
    firstnamelabel.grid(row=1, column=0)

    firstnameinput = tkr.Entry(top)
    firstnameinput.grid(row=1, column=1, padx=10, pady=10)

    lastnamelabel = tkr.Label(top, text="Last name:")
    lastnamelabel.grid(row=2, column=0)

    lastnameinput = tkr.Entry(top)
    lastnameinput.grid(row=2, column=1, padx=10, pady=10)

    associatenumberlabel = tkr.Label(top, text="Associate number:")
    associatenumberlabel.grid(row=3, column=0)

    associatenumberinput = tkr.Entry(top)
    associatenumberinput.grid(row=3, column=1, padx=10, pady=10)

    descriptionlabel = tkr.Label(top, text="Description of property:")
    descriptionlabel.grid(row=4, column=0)

    descriptioninput = tkr.Entry(top)
    descriptioninput.grid(row=4, column=1, padx=10, pady=10)

    # ========== For checking if all sections are filled out and adding them to the database ==============
    def adder():
        pnumber = passnumberinput.get().replace(" ", "")
        fname = firstnameinput.get().replace(" ", "")
        lname = lastnameinput.get().replace(" ", "")
        assocn = associatenumberinput.get().replace(" ", "")
        desc = descriptioninput.get().replace(" ", "")
        check = []

        if pnumber == str("") or fname == str("") or lname == str("") or assocn == str("") or desc == str(""):
            messagebox.showerror("Error", "All entries are not complete.")

        else:
            with conn:
                cur.execute("SELECT * FROM assign WHERE pass_num = ?", (pnumber,))
                x = cur.fetchall()
                check.append(x)

            if len(check[0]) > 0:
                messagebox.showwarning("Warning",
                                       "The pass you typed has already been assigned. Please choose another.")
                passnumberinput.delete(0, 'end')
            else:
                AddToDb(passnumberinput.get().replace(" ", ""), firstnameinput.get().replace(" ", ""),
                        lastnameinput.get().replace(" ", ""), associatenumberinput.get().replace(" ", ""),
                        descriptioninput.get(), conn).adddata()

                passnumberinput.delete(0, 'end')
                firstnameinput.delete(0, 'end')
                lastnameinput.delete(0, 'end')
                associatenumberinput.delete(0, 'end')
                descriptioninput.delete(0, 'end')

    def exit():
        top.destroy()

    addtobutton = tkr.Button(top, text="Add", width=8, height=2, command=adder)
    addtobutton.grid(row=0, column=2, padx=10, pady=10)
    exitbutton = tkr.Button(top, text="Exit",width=8, height=2, command=exit)
    exitbutton.grid(row=1, column=2, padx=10, pady=10)
    top.mainloop()

class EditPage:
    def __init__(self, root):
        self.root = root
        self.window()


    def center_window(self, w, h, top):
        ws = top.winfo_screenwidth()
        hs = top.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        top.geometry('+%d+%d' % (x, y))


    def search(self, pass_number, first_name, last_name, assoc_number, description):
        first_name.configure(state="normal")
        last_name.configure(state="normal")
        assoc_number.configure(state="normal")
        description.configure(state="normal")
        if pass_number.get().replace(" ","") == "":
            messagebox.showwarning("Warning", "No pass number entered.")
        else:
            with conn:
                cur.execute("SELECT * FROM assign WHERE pass_num = ?", (pass_number.get().replace(" ", ""),))
                x = cur.fetchall()
                for i in x:
                    name = i[1].split(" ")
                    firstname = name[0]
                    lastname = name[1]
                    first_name.insert(0, firstname)
                    last_name.insert(0, lastname)
                    assoc_number.insert(0, i[2])
                    description.insert(0, i[3])
        pass_number.configure(state="disabled")
        description.configure(state="disabled")


    def clear(self, passin, firstin, lastin, assoc_num, description):
        passin.focus()
        passin.configure(state="normal")
        firstin.configure(state="normal")
        lastin.configure(state="normal")
        assoc_num.configure(state="normal")
        description.configure(state="normal")
        passin.delete(0, 'end')
        firstin.delete(0, 'end')
        lastin.delete(0, 'end')
        assoc_num.delete(0, 'end')
        description.delete(0, 'end')
        firstin.configure(state="disabled")
        lastin.configure(state='disabled')
        assoc_num.configure(state="disabled")
        description.configure(state="disabled")


    def save(self, passin, firstin, lastin, assoc_num, description):
        passin.configure(state="normal")
        description.configure(state="normal")
        pass_in = passin.get()
        name = firstin.get().replace(" ", "") + " " + lastin.get().replace(" ", "")
        associate_num = assoc_num.get().replace(" ", "")
        desc = description.get()
        with conn:
            update = """UPDATE assign set pass_num = ?, name = ?, badge_num = ?, description = ? WHERE pass_num = ?"""
            data = (pass_in, name, associate_num, desc, pass_in)
            cur.execute(update, data)
            conn.commit()
        with conn:
            check_scan = []
            cur.execute("SELECT * FROM checkin WHERE pass_num = ?", (pass_in,))
            y = cur.fetchall()
            for i in y:
                check_scan.append(i)
                if len(check_scan[0]) > 0:
                    updatescan = """UPDATE scanlog set owner_name = ?, owner_badge = ? WHERE pass_num = ?"""
                    cur.execute(updatescan, (name, associate_num, pass_in))
                check_scan.clear()
        with conn:
            check_in = []
            cur.execute("SELECT * FROM checkin WHERE pass_num = ?", (pass_in,))
            z = cur.fetchall()
            for i in z:
                check_in.append(i)
                if len(check_in[0]) > 0:
                    cur.execute("""UPDATE checkin set owner_name = ?, owner_badge = ? WHERE pass_num = ?""", (name,
                                                                                                              associate_num,
                                                                                                              pass_in))
                check_in.clear()
        addtolistbox()
        self.clear(passin, firstin, lastin, assoc_num, description)


    def window(self):
        top = tkr.Toplevel(self.root)
        top.title("Edit Entry")
        pass_label = tkr.Label(top, text="Pass number:")
        pass_label.grid(row=1, column=0, padx=10, pady=10)
        pass_input = tkr.Entry(top)
        pass_input.configure(state="normal")
        pass_input.grid(row=1, column=1, padx=10, pady=10)
        first_name_label = tkr.Label(top, text="First name:")
        first_name_label.grid(row=2, column=0, padx=10, pady=10)
        first_name_input = tkr.Entry(top)
        first_name_input.configure(state="disabled")
        first_name_input.grid(row=2, column=1, padx=10, pady=10)
        last_name_label = tkr.Label(top, text="Last name:")
        last_name_label.grid(row=3, column=0, padx=10, pady=10)
        last_name_input = tkr.Entry(top)
        last_name_input.configure(state="disabled")
        last_name_input.grid(row=3, column=1, padx=10, pady=10)
        assoc_num_label = tkr.Label(top, text="Associate number:")
        assoc_num_label.grid(row=4, column=0, padx=10, pady=10)
        assoc_num_input = tkr.Entry(top)
        assoc_num_input.configure(state="disabled")
        assoc_num_input.grid(row=4, column=1, padx=10, pady=10)
        desc_label = tkr.Label(top, text="Description:")
        desc_label.grid(row=5, column=0, padx=10, pady=10)
        desc_input = tkr.Entry(top)
        desc_input.configure(state="disabled")
        desc_input.grid(row=5, column=1, padx=10, pady=10)
        searchbutt = tkr.Button(top, text="Search", width=6, height=2, command=lambda: self.search(pass_input, first_name_input,
                                                                                last_name_input, assoc_num_input,
                                                                                desc_input))
        searchbutt.grid(row=1, column=2, padx=5, pady=5)

        savebutton = tkr.Button(top, text="Save", width=6, height=2, command=lambda: self.save(pass_input, first_name_input,
                                                                               last_name_input, assoc_num_input,
                                                                               desc_input))
        savebutton.grid(row=2, column=2, padx=5, pady=5)
        clearbutton = tkr.Button(top, text="Clear", width=6, height=2,command=lambda: self.clear(pass_input, first_name_input,
                                                                               last_name_input, assoc_num_input,
                                                                               desc_input))
        clearbutton.grid(row=3, column=2, padx=5, pady=5)
        exitbutton = tkr.Button(top, text="Exit", width=6, height=2,command=lambda: top.destroy())
        exitbutton.grid(row=4, column=2, padx=5, pady=5)
        self.center_window(350, 250, top)
        pass_input.focus()


def search():
    top = tkr.Toplevel(root)
    top.title("Search")
    w = 825
    h = 550
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    top.geometry('+%d+%d' % (x, y))
    searchall = ttk.Treeview(top, height=25)
    searchall['columns'] = ("date", "time", "pass num", "name", "badge num", "owner name", "owner badge", "description")
    searchall.grid(row=0, column=1, columnspan=4, padx=10, pady=10)
    searchall.heading("#0", text="", anchor="w")
    searchall.column("#0", anchor="center", width=5, stretch="NO")
    searchall.heading("date", text="Date", anchor="w")
    searchall.column("date", anchor="center", minwidth=100, width=100)
    searchall.heading("time", text="Time", anchor="w")
    searchall.column("time", anchor="center", minwidth=70, width=70)
    searchall.heading("pass num", text="Pass number", anchor="w")
    searchall.column("pass num", anchor="center", minwidth=75, width=75)
    searchall.heading("name", text="Checked in by", anchor="w")
    searchall.column("name", anchor="center", minwidth=125, width=125)
    searchall.heading("badge num", text="Associate number", anchor="w")
    searchall.column("badge num", anchor="center", minwidth=75, width=75)
    searchall.heading("owner name", text="Belongs to", anchor="w")
    searchall.column("owner name", anchor="center", minwidth=125, width=125)
    searchall.heading("owner badge", text="Associate number", anchor="w")
    searchall.column("owner badge", anchor="center", minwidth=75, width=75)
    searchall.heading("description", text="Description", anchor="w")
    searchall.column("description", anchor="center", minwidth=150, width=150)
    exitbutton = tkr.Button(top, text="Exit", width=8, height=2,  command=lambda: top.destroy())
    exitbutton.grid(row=5, column=4, padx=5, pady=5)

    with conn:
        cur.execute("SELECT * FROM scanlog")
        results = cur.fetchall()
        for result in results:
            searchall.insert("", "end", text="", values=(result[0], result[1], result[2], result[3], result[4],
                                                         result[5], result[6], result[7]))
        conn.commit()
    check = []
    check.append(searchall.get_children())
    if len(check[0]) > 0:
        id = searchall.get_children()[-1]
        searchall.see(id)
        searchall.selection_set(id)


def addtolistbox():
    currentin.delete(*currentin.get_children())
    with conn:
        cur.execute("SELECT * FROM checkin")
        results = cur.fetchall()
        for result in results:
            currentin.insert("", "end", text="", values=(result[0], result[1], result[2], result[3], result[4],
                                                         result[5], result[6], result[7]))
        conn.commit()
    check = []
    check.append(currentin.get_children())
    if len(check[0]) > 0:
        id = currentin.get_children()[-1]
        currentin.see(id)
        currentin.selection_set(id)


# ================ For switching to the badge input entry on pressing enter =========================
def next(event):
    scanBadgeInput.focus()

def prev():
    scanPassInput.focus()


# ======================================= Main Window ====================================


# ===For adding space at the top of the window
tkr.Label(root, text="").grid(row=0, columnspan=4)

Spacer(1, 0).label()

scanPassLabel = tkr.Label(root, text="Scan pass")
scanPassLabel.grid(row=1, column=1)

scanPassInput = tkr.Entry(root)
scanPassInput.grid(row=2, column=1, padx=10, pady=10)
scanPassInput.bind('<Return>', next)

scanBadgeLabel = tkr.Label(root, text="Scan badge")
scanBadgeLabel.grid(row=1, column=3)

scanBadgeInput = tkr.Entry(root)
scanBadgeInput.grid(row=2, column=3, padx=10, pady=10)
scanBadgeInput.bind('<Return>', calladd)

Spacer(1, 4).label()

# ===For showing all current passes checked in
currentin = ttk.Treeview(root, height=15)
currentin['columns'] = ("date", "time", "pass num", "name", "badge num", "owner name", "owner badge", "description")
currentin.grid(row=5, columnspan=5, padx=10, pady=10)
currentin.heading("#0", text="", anchor="w")
currentin.column("#0", anchor="center", width=5, stretch="NO")
currentin.heading("date", text="Date", anchor="w")
currentin.column("date", anchor="center", minwidth=100, width=100)
currentin.heading("time", text="Time", anchor="w")
currentin.column("time", anchor="center", minwidth=70, width=70)
currentin.heading("pass num", text="Pass number", anchor="w")
currentin.column("pass num", anchor="center", minwidth=75, width=75)
currentin.heading("name", text="Checked in by", anchor="w")
currentin.column("name", anchor="center", minwidth=125, width=125)
currentin.heading("badge num", text="Associate number", anchor="w")
currentin.column("badge num", anchor="center", minwidth=75, width=75)
currentin.heading("owner name", text="Belongs to", anchor="w")
currentin.column("owner name", anchor="center", minwidth=125, width=125)
currentin.heading("owner badge", text="Associate number", anchor="w")
currentin.column("owner badge", anchor="center", minwidth=75, width=75)
currentin.heading("description", text="Description", anchor="w")
currentin.column("description", anchor="center", minwidth=150, width=150)

addbutton = tkr.Button(root, text="Add New", width=8, height=2, command=adduserwindow)
addbutton.grid(row=6, column=2, padx=10, pady=10)

searchbutton = tkr.Button(root, text="Search", width=8, height=2, command=search)
searchbutton.grid(row=6, column=1, padx=10, pady=10)

editbutton = tkr.Button(root, text="Edit", width=8, height=2, command=lambda: EditPage(root))
editbutton.grid(row=6, column=3)

deleteOld()
prev()
addtolistbox()

root.mainloop()

