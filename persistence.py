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
    
    def add_reminder(self, telegram_user_id, message, interval):
        unix = int(time.time())

        self.c.execute(
            """
            INSERT INTO reminder(
                user_id,
                message,
                created_time,
                interval_hours
            )
            VALUES(?, ?, ?, ?)
            """,
            (telegram_user_id, message, unix, interval)
        )