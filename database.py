import sqlite3

DB_FILE = 'users.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                days_before INTEGER,
                time_of_day TEXT,
                digest INTEGER,
                digest_day TEXT,
                digest_time TEXT,
                digest_range TEXT
            )
        ''')
        conn.commit()

def add_user(email, days_before, time_of_day, digest, digest_day, digest_time, digest_range):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO users (
                email, days_before, time_of_day, digest,
                digest_day, digest_time, digest_range
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, days_before, time_of_day, int(digest), digest_day, digest_time, digest_range))
        conn.commit()

def get_user_by_email(email):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = c.fetchone()
        if row:
            return {
                'email': row[0],
                'days_before': row[1],
                'time_of_day': row[2],
                'digest': bool(row[3]),
                'digest_day': row[4],
                'digest_time': row[5],
                'digest_range': row[6]
            }
        return None

def update_user(email, days_before, time_of_day, digest, digest_day, digest_time, digest_range):
    add_user(email, days_before, time_of_day, digest, digest_day, digest_time, digest_range)

def delete_user(email):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE email = ?', (email,))
        conn.commit()

def get_all_users():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        return c.fetchall()
