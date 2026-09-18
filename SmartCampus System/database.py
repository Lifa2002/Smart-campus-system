import sqlite3

DB_NAME = "campus_booking.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            campus_id INTEGER,
            FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campuses (
            campus_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            max_duration INTEGER NOT NULL,
            start_hour INTEGER NOT NULL,
            end_hour INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            campus_id INTEGER NOT NULL,
            FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            campus_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_hour INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM campuses")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO campuses (name, max_duration, start_hour, end_hour)
            VALUES (?, ?, ?, ?)
        ''', [
            ("Johannesburg Central", 3, 8, 17),
            ("Pretoria Campus", 2, 8, 16),
            ("Durban Campus", 4, 7, 18)
        ])
        
        cursor.executemany('''
            INSERT INTO users (username, password, role, campus_id)
            VALUES (?, ?, ?, ?)
        ''', [
            ("lecturer1", "pass123", "Lecturer", 1),
            ("admin_jhb", "admin123", "Campus Administrator", 1),
            ("admin_pta", "admin123", "Campus Administrator", 2),
            ("sys_operator", "sys123", "System Operator", None)
        ])
        
        cursor.executemany('''
            INSERT INTO resources (code, name, category, campus_id)
            VALUES (?, ?, ?, ?)
        ''', [
            ("JHB-LAB1", "Computer Lab A", "Laboratory", 1),
            ("JHB-PROJ1", "Epson Projector 4K", "Equipment", 1),
            ("PTA-SEM1", "Seminar Room 101", "Room", 2),
            ("DBN-LAB1", "Multimedia Lab", "Laboratory", 3)
        ])

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
