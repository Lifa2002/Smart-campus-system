import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

from database import init_db, get_connection
from models import Lecturer, CampusAdmin, SystemOperator, CampusPolicy

class SmartCampusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Campus Resource Booking System")
        self.geometry("850x600")
        
        init_db()
        
        self.current_user = None
        self.selected_campus_id = None
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_container()
        
        frame = ttk.Frame(self.container, padding=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(frame, text="Richfield Smart Campus System", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", pady=5)
        username_ent = ttk.Entry(frame)
        username_ent.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        password_ent = ttk.Entry(frame, show="*")
        password_ent.grid(row=2, column=1, pady=5)

        def login():
            uname = username_ent.get().strip()
            pwd = password_ent.get().strip()
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, role, campus_id FROM users WHERE username=? AND password=?", (uname, pwd))
            user_row = cursor.fetchone()
            conn.close()
            
            if user_row:
                uid, username, role, campus_id = user_row
                if role == "Lecturer":
                    self.current_user = Lecturer(uid, username, campus_id)
                elif role == "Campus Administrator":
                    self.current_user = CampusAdmin(uid, username, campus_id)
                elif role == "System Operator":
                    self.current_user = SystemOperator(uid, username)
                
                self.show_campus_selection()
            else:
                messagebox.showerror("Error", "Invalid username or password.")

        ttk.Button(frame, text="Login", command=login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Register as Lecturer", command=self.show_registration_screen).grid(row=4, column=0, columnspan=2)

    def show_registration_screen(self):
        self.clear_container()
        
        frame = ttk.Frame(self.container, padding=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(frame, text="Register Lecturer Account", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e", pady=5)
        uname_ent = ttk.Entry(frame)
        uname_ent.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e", pady=5)
        pwd_ent = ttk.Entry(frame, show="*")
        pwd_ent.grid(row=2, column=1, pady=5)

        def register():
            username = uname_ent.get().strip()
            password = pwd_ent.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "All fields are required.")
                return

            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'Lecturer')", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Account registered successfully! Please log in.")
                self.show_login_screen()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            finally:
                conn.close()

        ttk.Button(frame, text="Register", command=register).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Back to Login", command=self.show_login_screen).grid(row=4, column=0, columnspan=2)

    def show_campus_selection(self):
        self.clear_container()
        
        frame = ttk.Frame(self.container, padding=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(frame, text=f"Welcome, {self.current_user.username} ({self.current_user.role})", font=("Helvetica", 12, "italic")).pack(pady=5)
        ttk.Label(frame, text="Select Active Campus", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT campus_id, name FROM campuses")
        campuses = cursor.fetchall()
        conn.close()
        
        campus_dict = {name: cid for cid, name in campuses}
        campus_cb = ttk.Combobox(frame, values=list(campus_dict.keys()), state="readonly")
        campus_cb.pack(pady=10)
        if campuses:
            campus_cb.current(0)

        def proceed():
            self.selected_campus_id = campus_dict[campus_cb.get()]
            self.show_main_dashboard()

        ttk.Button(frame, text="Proceed", command=proceed).pack(pady=10)

    def show_main_dashboard(self):
        self.clear_container()
        
        policy = CampusPolicy.fetch_policy(self.selected_campus_id)
        
        header_frame = ttk.Frame(self.container, padding=10)
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text=f"User: {self.current_user.username} | Role: {self.current_user.role}", font=("Helvetica", 10, "bold")).pack(side="left")
        ttk.Button(header_frame, text="Logout", command=self.show_login_screen).pack(side="right")
        ttk.Button(header_frame, text="Switch Campus", command=self.show_campus_selection).pack(side="right", padx=5)
        
        policy_info = f"Active Campus: {policy.name} | Policy: Max {policy.max_duration}h/booking | Operating Hours: {policy.start_hour}:00 - {policy.end_hour}:00"
        ttk.Label(self.container, text=policy_info, font=("Helvetica", 10), background="#e1f5fe", padding=5).pack(fill="x")

        notebook = ttk.Notebook(self.container)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        if isinstance(self.current_user, Lecturer):
            self.setup_lecturer_tabs(notebook, policy)
        elif isinstance(self.current_user, CampusAdmin):
            self.setup_admin_tabs(notebook)
        elif isinstance(self.current_user, SystemOperator):
            self.setup_operator_tabs(notebook)

    def setup_lecturer_tabs(self, notebook, policy):
        book_tab = ttk.Frame(notebook, padding=10)
        notebook.add(book_tab, text="Book Resource")
        
        ttk.Label(book_tab, text="Available Resources").grid(row=0, column=0, columnspan=2, pady=5)
        
        res_tree = ttk.Treeview(book_tab, columns=("ID", "Code", "Name", "Category"), show="headings", height=5)
        res_tree.heading("ID", text="ID")
        res_tree.heading("Code", text="Code")
        res_tree.heading("Name", text="Name")
        res_tree.heading("Category", text="Category")
        res_tree.grid(row=1, column=0, columnspan=2, pady=5)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT resource_id, code, name, category FROM resources WHERE campus_id=?", (self.selected_campus_id,))
        for row in cursor.fetchall():
            res_tree.insert("", "end", values=row)
        conn.close()

        ttk.Label(book_tab, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="e", pady=5)
        date_ent = ttk.Entry(book_tab)
        date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_ent.grid(row=2, column=1, pady=5)

        ttk.Label(book_tab, text="Start Hour (24h format, e.g., 9):").grid(row=3, column=0, sticky="e", pady=5)
        hour_ent = ttk.Entry(book_tab)
        hour_ent.grid(row=3, column=1, pady=5)

        ttk.Label(book_tab, text="Duration (Hours):").grid(row=4, column=0, sticky="e", pady=5)
        dur_ent = ttk.Entry(book_tab)
        dur_ent.grid(row=4, column=1, pady=5)

        def make_booking():
            selected = res_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select a resource from the table.")
                return
            
            res_id = res_tree.item(selected[0])['values'][0]
            b_date = date_ent.get().strip()
            
            try:
                s_hour = int(hour_ent.get().strip())
                dur = int(dur_ent.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Start Hour and Duration must be valid integers.")
                return

            is_valid, msg = policy.validate_booking(s_hour, dur)
            if not is_valid:
                messagebox.showerror("Policy Constraint", msg)
                return

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bookings 
                WHERE resource_id=? AND booking_date=? 
                AND NOT (start_hour + duration <= ? OR start_hour >= ?)
            ''', (res_id, b_date, s_hour, s_hour + dur))
            
            if cursor.fetchone():
                messagebox.showerror("Booking Conflict", "Resource is already booked for the selected time slot.")
                conn.close()
                return

            cursor.execute('''
                INSERT INTO bookings (resource_id, user_id, campus_id, booking_date, start_hour, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (res_id, self.current_user.user_id, self.selected_campus_id, b_date, s_hour, dur))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Booking created successfully!")
            self.show_main_dashboard()

        ttk.Button(book_tab, text="Submit Booking", command=make_booking).grid(row=5, column=0, columnspan=2, pady=10)

        history_tab = ttk.Frame(notebook, padding=10)
        notebook.add(history_tab, text="My Bookings")

        hist_tree = ttk.Treeview(history_tab, columns=("ID", "Resource", "Date", "Start Hour", "Duration"), show="headings")
        hist_tree.heading("ID", text="Booking ID")
        hist_tree.heading("Resource", text="Resource Name")
        hist_tree.heading("Date", text="Date")
        hist_tree.heading("Start Hour", text="Start Hour")
        hist_tree.heading("Duration", text="Duration (hrs)")
        hist_tree.pack(fill="both", expand=True)

        def load_my_bookings():
            for item in hist_tree.get_children():
                hist_tree.delete(item)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.booking_id, r.name, b.booking_date, b.start_hour, b.duration 
                FROM bookings b
                JOIN resources r ON b.resource_id = r.resource_id
                WHERE b.user_id=?
            ''', (self.current_user.user_id,))
            for r in cursor.fetchall():
                hist_tree.insert("", "end", values=r)
            conn.close()

        def cancel_booking():
            selected = hist_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select a booking to cancel.")
                return
            b_id = hist_tree.item(selected[0])['values'][0]
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings WHERE booking_id=?", (b_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Booking canceled successfully.")
            load_my_bookings()

        ttk.Button(history_tab, text="Cancel Selected Booking", command=cancel_booking).pack(pady=5)
        load_my_bookings()

    def setup_admin_tabs(self, notebook):
        res_tab = ttk.Frame(notebook, padding=10)
        notebook.add(res_tab, text="Manage Resources")

        res_tree = ttk.Treeview(res_tab, columns=("ID", "Code", "Name", "Category"), show="headings")
        res_tree.heading("ID", text="Resource ID")
        res_tree.heading("Code", text="Code")
        res_tree.heading("Name", text="Name")
        res_tree.heading("Category", text="Category")
        res_tree.pack(fill="both", expand=True)

        def load_resources():
            for item in res_tree.get_children():
                res_tree.delete(item)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT resource_id, code, name, category FROM resources WHERE campus_id=?", (self.selected_campus_id,))
            for row in cursor.fetchall():
                res_tree.insert("", "end", values=row)
            conn.close()

        form_frame = ttk.Frame(res_tab, padding=10)
        form_frame.pack(fill="x")

        ttk.Label(form_frame, text="Code:").grid(row=0, column=0)
        code_ent = ttk.Entry(form_frame, width=10)
        code_ent.grid(row=0, column=1)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=2)
        name_ent = ttk.Entry(form_frame, width=15)
        name_ent.grid(row=0, column=3)

        ttk.Label(form_frame, text="Category:").grid(row=0, column=4)
        cat_ent = ttk.Entry(form_frame, width=15)
        cat_ent.grid(row=0, column=5)

        def add_resource():
            code = code_ent.get().strip()
            name = name_ent.get().strip()
            cat = cat_ent.get().strip()
            
            if not code or not name or not cat:
                messagebox.showerror("Error", "Fill in all fields.")
                return

            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO resources (code, name, category, campus_id) VALUES (?, ?, ?, ?)",
                               (code, name, cat, self.selected_campus_id))
                conn.commit()
                messagebox.showinfo("Success", "Resource added.")
                load_resources()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Resource code must be unique.")
            finally:
                conn.close()

        def delete_resource():
            selected = res_tree.selection()
            if not selected:
                messagebox.showerror("Error", "Select a resource to delete.")
                return
            rid = res_tree.item(selected[0])['values'][0]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM resources WHERE resource_id=?", (rid,))
            conn.commit()
            conn.close()
            load_resources()

        ttk.Button(form_frame, text="Add Resource", command=add_resource).grid(row=0, column=6, padx=5)
        ttk.Button(form_frame, text="Delete Resource", command=delete_resource).grid(row=0, column=7)
        load_resources()

        report_tab = ttk.Frame(notebook, padding=10)
        notebook.add(report_tab, text="Campus Usage Report")

        report_txt = tk.Text(report_tab, wrap="word", height=15)
        report_txt.pack(fill="both", expand=True)

        def generate_report():
            report_txt.delete("1.0", tk.END)
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE campus_id=?", (self.selected_campus_id,))
            total_bookings = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(duration) FROM bookings WHERE campus_id=?", (self.selected_campus_id,))
            avg_dur = cursor.fetchone()[0] or 0.0

            cursor.execute('''
                SELECT r.name, COUNT(b.booking_id) as count 
                FROM bookings b 
                JOIN resources r ON b.resource_id = r.resource_id
                WHERE b.campus_id=?
                GROUP BY b.resource_id ORDER BY count DESC LIMIT 1
            ''', (self.selected_campus_id,))
            top_res = cursor.fetchone()
            top_res_name = top_res[0] if top_res else "None"

            conn.close()

            report = f"--- CAMPUS USAGE REPORT ---\n"
            report += f"Total Bookings: {total_bookings}\n"
            report += f"Average Booking Duration: {avg_dur:.2f} hours\n"
            report += f"Most Used Resource: {top_res_name}\n"
            report_txt.insert("1.0", report)

        ttk.Button(report_tab, text="Generate Report", command=generate_report).pack(pady=5)

    def setup_operator_tabs(self, notebook):
        user_tab = ttk.Frame(notebook, padding=10)
        notebook.add(user_tab, text="Register Admin / Operator")

        ttk.Label(
            user_tab,
            text="Create Campus Administrator or System Operator",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)

        form = ttk.Frame(user_tab, padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        username_ent = ttk.Entry(form, width=25)
        username_ent.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        password_ent = ttk.Entry(form, width=25, show="*")
        password_ent.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Role:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        role_cb = ttk.Combobox(
            form,
            values=["Campus Administrator", "System Operator"],
            state="readonly",
            width=22
        )
        role_cb.grid(row=2, column=1, padx=5, pady=5)
        role_cb.current(0)

        ttk.Label(form, text="Campus:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        campus_cb = ttk.Combobox(form, state="readonly", width=22)
        campus_cb.grid(row=3, column=1, padx=5, pady=5)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT campus_id, name FROM campuses ORDER BY name")
        campus_rows = cursor.fetchall()
        conn.close()

        campus_dict = {name: cid for cid, name in campus_rows}
        campus_cb["values"] = list(campus_dict.keys())
        if campus_rows:
            campus_cb.current(0)

        def update_campus_state(event=None):
            if role_cb.get() == "System Operator":
                campus_cb.set("")
                campus_cb.configure(state="disabled")
            else:
                campus_cb.configure(state="readonly")
                if campus_rows and not campus_cb.get():
                    campus_cb.current(0)

        role_cb.bind("<<ComboboxSelected>>", update_campus_state)

        users_tree = ttk.Treeview(
            user_tab,
            columns=("ID", "Username", "Role", "Campus"),
            show="headings",
            height=8
        )

        for col, heading in [
            ("ID", "ID"),
            ("Username", "Username"),
            ("Role", "Role"),
            ("Campus", "Campus")
        ]:
            users_tree.heading(col, text=heading)

        users_tree.column("ID", width=50)
        users_tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_users():
            for item in users_tree.get_children():
                users_tree.delete(item)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.user_id, u.username, u.role,
                       COALESCE(c.name, 'All Campuses')
                FROM users u
                LEFT JOIN campuses c ON u.campus_id = c.campus_id
                WHERE u.role IN ('Campus Administrator', 'System Operator')
                ORDER BY u.role, u.username
            """)
            for row in cursor.fetchall():
                users_tree.insert("", "end", values=row)
            conn.close()

        def register_staff():
            username = username_ent.get().strip()
            password = password_ent.get().strip()
            role = role_cb.get()

            if not username or not password or not role:
                messagebox.showerror("Error", "Username, password and role are required.")
                return

            campus_id = None

            if role == "Campus Administrator":
                if not campus_cb.get():
                    messagebox.showerror(
                        "Error",
                        "Please select a campus for the Campus Administrator."
                    )
                    return
                campus_id = campus_dict[campus_cb.get()]

            conn = get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO users (username, password, role, campus_id) VALUES (?, ?, ?, ?)",
                    (username, password, role, campus_id)
                )
                conn.commit()

                messagebox.showinfo(
                    "Success",
                    f"{role} account '{username}' registered successfully."
                )

                username_ent.delete(0, tk.END)
                password_ent.delete(0, tk.END)
                load_users()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")

            finally:
                conn.close()

        def delete_staff():
            selected = users_tree.selection()

            if not selected:
                messagebox.showerror("Error", "Select an account to delete.")
                return

            uid = users_tree.item(selected[0])["values"][0]
            username = users_tree.item(selected[0])["values"][1]

            if uid == self.current_user.user_id:
                messagebox.showerror(
                    "Error",
                    "You cannot delete the account currently being used."
                )
                return

            if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete account '{username}'?"
            ):
                return

            conn = get_connection()
            cursor = conn.cursor()

            try:
                cursor.execute("DELETE FROM users WHERE user_id=?", (uid,))
                conn.commit()
                messagebox.showinfo("Success", "Account deleted.")
                load_users()

            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Error",
                    "This account cannot be deleted because it has existing bookings."
                )

            finally:
                conn.close()

        button_frame = ttk.Frame(user_tab)
        button_frame.pack(pady=5)

        ttk.Button(
            button_frame,
            text="Register Account",
            command=register_staff
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Delete Selected",
            command=delete_staff
        ).pack(side="left", padx=5)

        load_users()

        report_tab = ttk.Frame(notebook, padding=10)
        notebook.add(report_tab, text="Cross-Campus Comparison")

        report_txt = tk.Text(report_tab, wrap="word", height=15)
        report_txt.pack(fill="both", expand=True)

        def generate_cross_report():
            report_txt.delete("1.0", tk.END)
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT campus_id, name FROM campuses")
            campuses = cursor.fetchall()

            report = "=== CROSS-CAMPUS COMPARATIVE REPORT ===\n\n"
            for cid, cname in campuses:
                cursor.execute("SELECT COUNT(*), AVG(duration) FROM bookings WHERE campus_id=?", (cid,))
                count, avg_d = cursor.fetchone()
                avg_d = avg_d if avg_d else 0.0
                report += f"Campus: {cname}\n"
                report += f"  - Total Bookings: {count}\n"
                report += f"  - Avg Duration: {avg_d:.2f} hrs\n\n"

            conn.close()
            report_txt.insert("1.0", report)

        ttk.Button(report_tab, text="Generate System-Wide Report", command=generate_cross_report).pack(pady=5)

if __name__ == "__main__":
    app = SmartCampusApp()
    app.mainloop()
