import sqlite3
from database import get_connection

class User:
    def __init__(self, user_id, username, role, campus_id=None):
        self._user_id = user_id
        self._username = username
        self._role = role
        self._campus_id = campus_id

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def role(self):
        return self._role

    @property
    def campus_id(self):
        return self._campus_id


class Lecturer(User):
    def __init__(self, user_id, username, campus_id=None):
        super().__init__(user_id, username, "Lecturer", campus_id)


class CampusAdmin(User):
    def __init__(self, user_id, username, campus_id):
        super().__init__(user_id, username, "Campus Administrator", campus_id)


class SystemOperator(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, "System Operator", None)


class CampusPolicy:
    def __init__(self, campus_id, name, max_duration, start_hour, end_hour):
        self.campus_id = campus_id
        self.name = name
        self.max_duration = max_duration
        self.start_hour = start_hour
        self.end_hour = end_hour

    def validate_booking(self, start_hour, duration):
        if duration > self.max_duration:
            return False, f"Maximum booking duration for {self.name} is {self.max_duration} hour(s)."
        if start_hour < self.start_hour or (start_hour + duration) > self.end_hour:
            return False, f"Operating hours for {self.name} are {self.start_hour}:00 - {self.end_hour}:00."
        return True, "Valid"

    @staticmethod
    def fetch_policy(campus_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT campus_id, name, max_duration, start_hour, end_hour FROM campuses WHERE campus_id=?", (campus_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return CampusPolicy(row[0], row[1], row[2], row[3], row[4])
        return None
