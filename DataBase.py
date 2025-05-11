import sqlite3
import hashlib
import secrets

ACTIVITY_DB = 'user_activity.db'
DEMO_DB = 'demo.db' #temp database

def init_db():
    conn = sqlite3.connect(ACTIVITY_DB)
    cursor = conn.cursor()
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS user_activity (
        id INTEGER PRIMARY KEY,
        user_name TEXT,
        message TEXT,
        timestamp TEXT)"""
    )
    # Auth table for local user credentials
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_auth (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT)"""
    )
    conn.commit()
    conn.close()

def log_activity(user:str, message:str, timestamp:str = None):
    # insert new activity record
    timestamp = timestamp or __import__('datetime').datetime.now().isoformat()
    conn = sqlite3.connect(ACTIVITY_DB)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_activity (user_name, message, timestamp)'
                   (user, message, timestamp)
    )
    conn.commit()
    conn.close()

def create_user(username: str, password: str, role: str = None) ->bool:
    """Register new user with hashed password and random salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256'. password.encode(),salt.encode(),10000).hex()
    try:
        conn = sqlite3.connect(ACTIVITY_DB)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO user_auth (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
            (username, pwd_hash, salt, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    """Verify provided password against stored hash and salt"""
    conn = sqlite3.connect(ACTIVITY_DB)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT password_hash, salt FROM user_auth WHERE username = ?',
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    stored_hash, salt = row
    # Recreate the hash with the same salt and compare
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100000
    ).hex()
    return pwd_hash == stored_hash

# Temp function build out based on actual database
def query_books(filters:dict )->list:
    # Build and execute SQL query on DEMO_DB based on filters
    pass
