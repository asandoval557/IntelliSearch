import sqlite3

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

# Temp function build out based on actual database
def query_books(filters:dict )->list:
    # Build and execute SQL query on DEMO_DB based on filters
    pass
