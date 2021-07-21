import sqlite3
import time


class DBConn:
    """ SQLite3 DB connection interface """
    def __init__(self):
        path = "./reminder.db"
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()

        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS
            user(
                telegram_id INTEGER PRIMARY KEY,
                time INTEGER,
                first_name TEXT
                )
            """
        )

        self.c.execute(
            """
            CREATE TABLE IF NOT EXISTS
            reminder(
                reminder_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                created_time INTEGER,
                interval_hours INTEGER,
                active INTEGER,
                FOREIGN KEY (user_id) REFERENCES user(telegram_id)
            )
            """
        )

    def commit(self):
        """ Commit all changes made """
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.c.close()
        self.conn.close()

    def __enter__(self):
        # Needed for the Destructor
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Destructor: closes connection and cursor """
        self.close()

    def add_user(self, first_name, telegram_id):
        unix = int(time.time())

        self.c.execute(
            """
            INSERT INTO user(
                telegram_id,
                time,
                first_name
            )
            VALUES(?, ?, ?)
            """,
            (telegram_id, unix, first_name),
        )
    
    def add_reminder(self, telegram_user_id, message, interval_hours):
        unix = int(time.time())

        self.c.execute(
            """
            INSERT INTO reminder(
                user_id,
                message,
                created_time,
                interval_hours,
                active
            )
            VALUES(?, ?, ?, ?, 1)
            """,
            (telegram_user_id, message, unix, interval_hours)
        )
    
    def get_all_active_reminders(self):
        """Returns all active reminders"""
        self.c.execute("""
            SELECT message, created_time, interval_hours, user_id
            FROM reminder
            WHERE active = 1
        """)

        data = self.c.fetchall()
        return data

    def get_active_reminders(self, user_id):
        """Returns active reminders of a user"""
        self.c.execute("""
            SELECT message, interval_hours, reminder_id
            FROM reminder
            WHERE active = 1 AND user_id = ?
        """, [user_id])

        data = self.c.fetchall()
        return data
    
    def inactivate_reminder(self, id):
        self.c.execute("""
            UPDATE reminder
            SET active = 0
            WHERE
                reminder_id = ?
        """, [id])