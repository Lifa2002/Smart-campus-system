# Smart Campus Resource Booking System

A desktop application built using Python, Tkinter, and SQLite3 for managing academic resources across multiple campuses.

## Instructions:
1. Run `python main.py` to start the application.
2. Log in using default credentials:
   - **Lecturer:** `lecturer1` / `pass123`
   - **Campus Admin:** `admin_jhb` / `admin123`
   - **System Operator:** `sys_operator` / `sys123`


## Admin / Operator Registration


User Roles

The system has the following main user roles:

System Operator

The System Operator has the highest level of administrative access.

A System Operator can:

Manage users.
Register Campus Administrators.
Register other System Operators.
View registered administrators and operators.
Delete administrator and operator accounts.
Manage information across all campuses.
Campus Administrator

A Campus Administrator is responsible for managing a specific campus.

A Campus Administrator:

Is assigned to a specific campus.
Can access the administrative functions available to their role.
Uses their own username and password to access the system.

Lecturer

Lecturers use the system for lecturer-related activities.

Lecturers can register their own accounts through the registration option on the login screen and then log in using their registered credentials.
