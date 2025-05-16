import sqlite3
import hashlib
import secrets
from datetime import datetime

# Database file paths
activity_db = 'user_activity.db'
auth_db = 'user_auth.db'
demo_db = 'demo_books.db'


def init_db():
    """Initialize all required databases and tables."""
    # 1) Activity DB
    conn = sqlite3.connect(activity_db)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_activity'")
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create table with correct columns
        cursor.execute(
            '''
            CREATE TABLE user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            '''
        )
    else:
        # Check if username column exists
        try:
            cursor.execute("SELECT username FROM user_activity LIMIT 1")
        except sqlite3.OperationalError:
            # Add username column if it doesn't exist
            cursor.execute("ALTER TABLE user_activity ADD COLUMN username TEXT")

    conn.commit()
    conn.close()

    # 2) Auth DB
    conn = sqlite3.connect(auth_db)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS user_auth (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT
        );
        '''
    )
    conn.commit()
    conn.close()

    # 3) Demo DB
    conn = sqlite3.connect(demo_db)
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            publication_year INTEGER NOT NULL
        );
        '''
    )
    conn.commit()
    conn.close()

def log_activity(username: str, message: str, timestamp: str = None):
    """Log a user interaction in the activity database."""
    ts = timestamp or datetime.now().isoformat()
    conn = sqlite3.connect(activity_db)
    cursor = conn.cursor()

    # Get column names to determine correct insert statement
    cursor.execute("PRAGMA table_info(user_activity)")
    columns = [column[1] for column in cursor.fetchall()]

    if "username" in columns:
        cursor.execute(
            'INSERT INTO user_activity (username, message, timestamp) VALUES (?, ?, ?)',
            (username, message, ts)
        )
    else:
        # If no username column, use the schema that exists
        cursor.execute(
            'INSERT INTO user_activity (message, timestamp) VALUES (?, ?)',
            (message, ts)
        )

    conn.commit()
    conn.close()


def create_user(username: str, password: str, role: str = None) -> bool:
    """Register a new user in the auth database. Returns False if username exists."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100000
    ).hex()
    try:
        conn = sqlite3.connect(auth_db)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO user_auth (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
            (username, pwd_hash, salt, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    finally:
        conn.close()


def verify_user(username: str, password: str) -> bool:
    """Verify a user's password against the stored hash in the auth database."""
    conn = sqlite3.connect(auth_db)
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
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode(), salt.encode(), 100000
    ).hex()
    return pwd_hash == stored_hash


def query_books(filters: dict) -> list:
    """Retrieve books from demo database based on provided filters dict."""
    # TODO: Build SQL from filters (genre, years, etc.) and return results
    conn = sqlite3.connect(demo_db)
    cursor = conn.cursor()
    # simple fallback all rows
    cursor.execute('SELECT title, genre, publication_year FROM books')
    results = cursor.fetchall()
    conn.close()
    return results
