# payroll_gui_fixed_v2.py
import sqlite3
from tkinter import *
from tkinter import ttk, messagebox

# ---------- Database ----------
conn = sqlite3.connect("payroll.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT,
    base_salary REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    working_days INTEGER DEFAULT 0,
    leaves INTEGER DEFAULT 0,
    bonus REAL DEFAULT 0,
    deduction REAL DEFAULT 0,
    UNIQUE(emp_id, month),
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS salary_advance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payslips(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    gross REAL,
    deductions REAL,
    net REAL,
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
)
""")
conn.commit()

# ---------- Root ----------
root = Tk()
root.title("Payroll Management System (Fixed v2)")
root.geometry("1000x700")
root.configure(bg="#f3f8ff")

# ---------- Notebook / Tabs ----------
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=8, pady=8)

tab_emp = Frame(notebook, bg="#f6fbff")
tab_att = Frame(notebook, bg="#f6fbff")
tab_sal = Frame(notebook, bg="#f6fbff")
tab_adv = Frame(notebook, bg="#f6fbff")

notebook.add(tab_emp, text="Employees")
notebook.add(tab_att, text="Attendance")
notebook.add(tab_sal, text="Salary & Payslips")
notebook.add(tab_adv, text="Salary Advances")

# ---------- Helpers ----------
def safe_float(s, default=0.0):
    try:
        return float(s)
    except:
        return default

def safe_int(s, default=0):
    try:
        return int(float(s))
    except:
        return default

# ---------- EMPLOYEES TAB ----------
Label(tab_emp, text="Add / Update Employee", font=("Arial", 12, "bold"), bg="#f6fbff").grid(row=0, column=0, columnspan=4, pady=6)

Label(tab_emp, text="Name:", bg="#f6fbff").grid(row=1, column=0, sticky=E, padx=6, pady=4)
Label(tab_emp, text="Position:", bg="#f6fbff").grid(row=2, column=0, sticky=E, padx=6, pady=4)
Label(tab_emp, text="Base Salary (₹):", bg="#f6fbff").grid(row=3, column=0, sticky=E, padx=6, pady=4)

emp_name = StringVar()
emp_position = StringVar()
emp_salary = StringVar()
emp_search = StringVar()

Entry(tab_emp, textvariable=emp_name, width=30).grid(row=1, column=1, padx=6, pady=4)
Entry(tab_emp, textvariable=emp_position, width=30).grid(row=2, column=1, padx=6, pady=4)
Entry(tab_emp, textvariable=emp_salary, width=30).grid(row=3, column=1, padx=6, pady=4)

def add_employee():
    name = emp_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Name is required")
        return
    base = safe_float(emp_salary.get(), 0.0)
    cursor.execute("INSERT INTO employees (name, position, base_salary) VALUES (?, ?, ?)",
                   (name, emp_position.get().strip(), base))
    conn.commit()
    messagebox.showinfo("Success", "Employee added")
    emp_name.set(""); emp_position.set(""); emp_salary.set("")
    view_employees()

def update_employee():
    sel = emp_table.focus()
    if not sel:
        messagebox.showwarning("Select", "Select an employee row to update from table below")
        return
    values = emp_table.item(sel, "values")
    emp_id = values[0]
    name = emp_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Name required for update")
        return
    base = safe_float(emp_salary.get(), 0.0)
    cursor.execute("UPDATE employees SET name=?, position=?, base_salary=? WHERE emp_id=?", (name, emp_position.get().strip(), base, emp_id))
    conn.commit()
    messagebox.showinfo("Updated", "Employee updated")
    view_employees()

def delete_employee():
    sel = emp_table.focus()
    if not sel:
        messagebox.showwarning("Select", "Select an employee row to delete")
        return
    values = emp_table.item(sel, "values")
    emp_id = values[0]
    if messagebox.askyesno("Confirm", f"Delete employee ID {emp_id}?"):
        cursor.execute("DELETE FROM employees WHERE emp_id=?", (emp_id,))
        conn.commit()
        view_employees()
        view_attendance()
        view_advances()
        view_payslips()

Button(tab_emp, text="Add Employee", command=add_employee, bg="#2e86de", fg="white", width=15).grid(row=4, column=1, pady=6, sticky=W)
Button(tab_emp, text="Update Selected", command=update_employee, bg="#16a085", fg="white", width=15).grid(row=4, column=1, pady=6, sticky=E)
Button(tab_emp, text="Delete Selected", command=delete_employee, bg="#c0392b", fg="white", width=15).grid(row=4, column=2, pady=6)

# Search
Label(tab_emp, text="Search (ID or Name):", bg="#f6fbff").grid(row=5, column=0, sticky=E, padx=6)
Entry(tab_emp, textvariable=emp_search, width=30).grid(row=5, column=1, padx=6)

def search_employee():
    term = emp_search.get().strip()
    for row in emp_table.get_children():
        emp_table.delete(row)
    if term == "":
        view_employees()
        return
    # try id first (exact)
    if term.isdigit():
        cursor.execute("SELECT * FROM employees WHERE emp_id=?", (int(term),))
    else:
        # case-insensitive search for name
        cursor.execute("SELECT * FROM employees WHERE LOWER(name) LIKE ?", ('%'+term.lower()+'%',))
    rows = cursor.fetchall()
    for row in rows:
        emp_table.insert("", END, values=row)

Button(tab_emp, text="Search", command=search_employee, width=12).grid(row=5, column=2)
Button(tab_emp, text="Show All", command=lambda: (emp_search.set(""), view_employees()), width=12).grid(row=5, column=3)

# Employee table
emp_table = ttk.Treeview(tab_emp, columns=("ID","Name","Position","BaseSalary"), show="headings", height=10)
for col in emp_table["columns"]:
    emp_table.heading(col, text=col)
    emp_table.column(col, width=150)
emp_table.grid(row=6, column=0, columnspan=4, padx=8, pady=10, sticky='nsew')

def view_employees():
    for r in emp_table.get_children(): emp_table.delete(r)
    cursor.execute("SELECT * FROM employees ORDER BY emp_id")
    for row in cursor.fetchall():
        emp_table.insert("", END, values=row)

# On row select, populate fields
def on_emp_select(event):
    sel = emp_table.focus()
    if not sel: return
    vals = emp_table.item(sel, "values")
    emp_name.set(vals[1])
    emp_position.set(vals[2])
    emp_salary.set(vals[3])

emp_table.bind("<<TreeviewSelect>>", on_emp_select)
view_employees()

# ---------- ATTENDANCE TAB ----------
Label(tab_att, text="Add / Update Attendance (unique per emp+month)", font=("Arial", 12, "bold"), bg="#f6fbff").grid(row=0, column=0, columnspan=6, pady=6)

att_emp_id = StringVar()
att_month = StringVar()
att_working = StringVar()
att_leaves = StringVar()
att_bonus = StringVar()
att_deduction = StringVar()

labels = ["Emp ID:", "Month (e.g. 2025-10):", "Working Days:", "Leaves:", "Bonus:", "Deduction:"]
vars_ = [att_emp_id, att_month, att_working, att_leaves, att_bonus, att_deduction]
for i, text in enumerate(labels):
    Label(tab_att, text=text, bg="#f6fbff").grid(row=1+i, column=0, sticky=E, padx=6, pady=4)
    Entry(tab_att, textvariable=vars_[i], width=20).grid(row=1+i, column=1, padx=6, pady=4)

def add_or_update_attendance():
    empid = safe_int(att_emp_id.get(), None)
    if empid is None:
        messagebox.showerror("Error", "Employee ID required")
        return
    # check employee exists
    cursor.execute("SELECT 1 FROM employees WHERE emp_id=?", (empid,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", f"Employee ID {empid} not found")
        return
    month = att_month.get().strip()
    if not month:
        messagebox.showerror("Error", "Month required")
        return
    work = safe_int(att_working.get(), 0)
    leaves = safe_int(att_leaves.get(), 0)
    bonus = safe_float(att_bonus.get(), 0.0)
    deduction = safe_float(att_deduction.get(), 0.0)
    # try insert, if conflict -> update
    try:
        cursor.execute("INSERT INTO attendance (emp_id, month, working_days, leaves, bonus, deduction) VALUES (?, ?, ?, ?, ?, ?)",
                       (empid, month, work, leaves, bonus, deduction))
    except sqlite3.IntegrityError:
        cursor.execute("UPDATE attendance SET working_days=?, leaves=?, bonus=?, deduction=? WHERE emp_id=? AND month=?",
                       (work, leaves, bonus, deduction, empid, month))
    conn.commit()
    messagebox.showinfo("Saved", "Attendance saved")
    clear_att_fields()
    view_attendance()

def clear_att_fields():
    att_emp_id.set(""); att_month.set(""); att_working.set(""); att_leaves.set(""); att_bonus.set(""); att_deduction.set("")

Button(tab_att, text="Add / Update Attendance", command=add_or_update_attendance, bg="#2e86de", fg="white").grid(row=7, column=1, pady=8)
Button(tab_att, text="Refresh Table", command=lambda: view_attendance(), bg="#27ae60", fg="white").grid(row=7, column=0, pady=8)
Button(tab_att, text="Show All", command=lambda: (att_emp_id.set(""), att_month.set(""), view_attendance()), bg="#95a5a6", fg="white").grid(row=7, column=2, pady=8)

# attendance table: show id, emp_id, emp_name, month, working, leaves, bonus, deduction
att_table = ttk.Treeview(tab_att, columns=("ID","EmpID","Name","Month","Working","Leaves","Bonus","Deduction"), show="headings", height=12)
for col in att_table["columns"]:
    att_table.heading(col, text=col)
    att_table.column(col, width=110)
att_table.grid(row=8, column=0, columnspan=6, padx=8, pady=8, sticky='nsew')

def view_attendance():
    for r in att_table.get_children(): att_table.delete(r)
    cursor.execute("""
        SELECT a.id, a.emp_id, e.name, a.month, a.working_days, a.leaves, a.bonus, a.deduction
        FROM attendance a
        LEFT JOIN employees e ON a.emp_id = e.emp_id
        ORDER BY a.id DESC
    """)
    for row in cursor.fetchall():
        att_table.insert("", END, values=row)

view_attendance()

# ---------- SALARY & PAYSLIPS TAB ----------
Label(tab_sal, text="Calculate Salary and Generate Payslip", font=("Arial", 12, "bold"), bg="#f6fbff").grid(row=0, column=0, columnspan=4, pady=6)

calc_emp_id = StringVar()
calc_month = StringVar()
payslip_display = StringVar()

Label(tab_sal, text="Emp ID:", bg="#f6fbff").grid(row=1, column=0, sticky=E, padx=6, pady=4)
Entry(tab_sal, textvariable=calc_emp_id, width=18).grid(row=1, column=1, padx=6, pady=4)
Label(tab_sal, text="Month:", bg="#f6fbff").grid(row=2, column=0, sticky=E, padx=6, pady=4)
Entry(tab_sal, textvariable=calc_month, width=18).grid(row=2, column=1, padx=6, pady=4)

def calculate_and_save_payslip():
    empid = safe_int(calc_emp_id.get(), None)
    if empid is None:
        messagebox.showerror("Error", "Emp ID required")
        return
    month = calc_month.get().strip()
    if not month:
        messagebox.showerror("Error", "Month required")
        return
    # fetch employee + attendance
    cursor.execute("SELECT name, base_salary FROM employees WHERE emp_id=?", (empid,))
    emp = cursor.fetchone()
    if not emp:
        messagebox.showerror("Error", "Employee not found")
        return
    cursor.execute("SELECT working_days, leaves, bonus, deduction FROM attendance WHERE emp_id=? AND month=?", (empid, month))
    att = cursor.fetchone()
    if not att:
        messagebox.showerror("Error", "Attendance for this emp/month not found")
        return
    name, base_salary = emp
    work, leaves, bonus, deduction = att
    base_salary = safe_float(base_salary, 0.0)
    work = safe_int(work, 0)
    leaves = safe_int(leaves, 0)
    bonus = safe_float(bonus, 0.0)
    deduction = safe_float(deduction, 0.0)
    per_day = base_salary / 30.0
    gross = (work * per_day) + bonus
    deductions_total = deduction + (leaves * per_day)
    net = gross - deductions_total
    # save payslip record
    cursor.execute("INSERT INTO payslips (emp_id, month, gross, deductions, net) VALUES (?, ?, ?, ?, ?)",
                   (empid, month, round(gross,2), round(deductions_total,2), round(net,2)))
    conn.commit()
    payslip_display.set(f"Payslip for {name} ({empid}) - {month}\nGross: ₹{round(gross,2)}\nDeductions: ₹{round(deductions_total,2)}\nNet Pay: ₹{round(net,2)}")
    view_payslips()
    messagebox.showinfo("Payslip Generated", "Payslip record created and displayed below.")

Button(tab_sal, text="Generate Payslip", command=calculate_and_save_payslip, bg="#8e44ad", fg="white", width=18).grid(row=3, column=1, pady=8)
Label(tab_sal, textvariable=payslip_display, bg="#f6fbff", justify=LEFT, font=("Arial", 11)).grid(row=4, column=0, columnspan=2, padx=8, pady=6)

# Payslips table
payslip_table = ttk.Treeview(tab_sal, columns=("ID","EmpID","Name","Month","Gross","Deductions","Net"), show="headings", height=12)
for col in payslip_table["columns"]:
    payslip_table.heading(col, text=col)
    payslip_table.column(col, width=110)
payslip_table.grid(row=6, column=0, columnspan=4, padx=8, pady=8, sticky='nsew')

def view_payslips():
    for r in payslip_table.get_children(): payslip_table.delete(r)
    cursor.execute("""
        SELECT p.id, p.emp_id, e.name, p.month, p.gross, p.deductions, p.net
        FROM payslips p
        LEFT JOIN employees e ON p.emp_id = e.emp_id
        ORDER BY p.id DESC
    """)
    for row in cursor.fetchall():
        payslip_table.insert("", END, values=row)

view_payslips()

# ---------- SALARY ADVANCES TAB ----------
Label(tab_adv, text="Request / Approve Salary Advance", font=("Arial", 12, "bold"), bg="#f6fbff").grid(row=0, column=0, columnspan=4, pady=6)

adv_emp_id = StringVar()
adv_month = StringVar()
adv_amount = StringVar()

Label(tab_adv, text="Emp ID:", bg="#f6fbff").grid(row=1, column=0, sticky=E, padx=6)
Entry(tab_adv, textvariable=adv_emp_id, width=20).grid(row=1, column=1)
Label(tab_adv, text="Month:", bg="#f6fbff").grid(row=2, column=0, sticky=E, padx=6)
Entry(tab_adv, textvariable=adv_month, width=20).grid(row=2, column=1)
Label(tab_adv, text="Amount (₹):", bg="#f6fbff").grid(row=3, column=0, sticky=E, padx=6)
Entry(tab_adv, textvariable=adv_amount, width=20).grid(row=3, column=1)

def request_advance():
    empid = safe_int(adv_emp_id.get(), None)
    if empid is None:
        messagebox.showerror("Error", "Emp ID required")
        return
    cursor.execute("SELECT 1 FROM employees WHERE emp_id=?", (empid,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Employee not found")
        return
    month = adv_month.get().strip()
    if not month:
        messagebox.showerror("Error", "Month required")
        return
    amt = safe_float(adv_amount.get(), 0.0)
    cursor.execute("INSERT INTO salary_advance (emp_id, month, amount, status) VALUES (?, ?, ?, ?)", (empid, month, amt, "Pending"))
    conn.commit()
    messagebox.showinfo("Requested", "Advance request saved")
    adv_emp_id.set(""); adv_month.set(""); adv_amount.set("")
    view_advances()

def approve_advance():
    sel = adv_table.focus()
    if not sel:
        messagebox.showwarning("Select", "Select an advance request to approve from table below")
        return
    vals = adv_table.item(sel, "values")
    adv_id = vals[0]
    cursor.execute("UPDATE salary_advance SET status='Approved' WHERE id=?", (adv_id,))
    conn.commit()
    messagebox.showinfo("Approved", "Advance approved")
    view_advances()

adv_table = ttk.Treeview(tab_adv, columns=("ID","EmpID","Name","Month","Amount","Status"), show="headings", height=14)
for col in adv_table["columns"]:
    adv_table.heading(col, text=col)
    adv_table.column(col, width=110)
adv_table.grid(row=5, column=0, columnspan=4, padx=8, pady=8, sticky='nsew')

Button(tab_adv, text="Request Advance", command=request_advance, bg="#f39c12", fg="white", width=16).grid(row=4, column=1, pady=6)
Button(tab_adv, text="Approve Selected", command=approve_advance, bg="#16a085", fg="white", width=16).grid(row=4, column=2, pady=6)

def view_advances():
    for r in adv_table.get_children(): adv_table.delete(r)
    cursor.execute("""
        SELECT s.id, s.emp_id, e.name, s.month, s.amount, s.status
        FROM salary_advance s
        LEFT JOIN employees e ON s.emp_id = e.emp_id
        ORDER BY s.id DESC
    """)
    for row in cursor.fetchall():
        adv_table.insert("", END, values=row)

view_advances()

# ---------- Finalize ----------
root.mainloop()
conn.close()
