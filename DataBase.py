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
    conn.commit()
    conn.close()

def log_activity(user:str, message:str):
    # insert new activity record
    pass

# Temp function build out based on actual database
def query_books(filters:dict )->list:
    # Build and execute SQL query on DEMO_DB based on filters
    pass
