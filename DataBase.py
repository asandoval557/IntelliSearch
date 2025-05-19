import sqlite3
import hashlib
import secrets
from datetime import datetime
import random

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

def populate_demo_books(count = 200, books=None):
    """ Populate the books database with random book entries.
    Args:
        count: Number of random books to generate.(default: 200)"""
    conn = sqlite3.connect(demo_db)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM books")

    # Sample data for random generation
    genres = ["Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance",
        "Historical Fiction", "Non-Fiction", "Biography", "Self-Help",
        "Horror", "Adventure", "Children's", "Young Adult", "Poetry",
        "Drama", "Classic", "Dystopian", "Memoir", "Philosophy", "Science"]

    title_prefixes = ["The", "A", "Secret", "Hidden", "Lost", "Last", "First", "New",
        "Ancient", "Final", "Eternal", "Forgotten", "Mysterious", "Dark",
        "Light", "Shadow", "Silent", "Wild", "Crimson", "Golden", "Silver"]

    title_subjects = ["Garden", "Mountain", "Sea", "River", "Forest", "City", "Star", "Moon",
        "Sun", "Kingdom", "Empire", "Journey", "Adventure", "Quest", "Legacy",
        "Mystery", "Secret", "Dream", "Nightmare", "Paradise", "World", "Universe",
        "Chronicle", "Story", "Tale", "Legend", "Myth", "Prophecy", "War", "Battle",
        "Hero", "Knight", "King", "Queen", "Prince", "Princess", "Wizard", "Witch",
        "Dragon", "Ghost", "Soul", "Heart", "Mind", "Life", "Death", "Destiny"]

    title_suffixes = ["of Time", "of Destiny", "of Fate", "of Shadows", "of Light", "of Dreams",
        "of Fire", "of Ice", "of Water", "of Earth", "of Wind", "in Space",
        "in the Dark", "in the Light", "in Winter", "in Summer", "at Dawn",
        "at Dusk", "in Ruins", "of the Past", "of the Future", "Reborn",
        "Awakened", "Unleashed", "Revealed", "Forgotten", "Remembered"]

    authors_first_names = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Jessica",
        "William", "Elizabeth", "James", "Olivia", "Richard", "Sophia", "Thomas",
        "Emma", "Charles", "Ava", "Daniel", "Mia", "Matthew", "Isabella", "Joseph",
        "Amelia", "Christopher", "Abigail", "Andrew", "Charlotte", "Joshua", "Harper"]

    authors_last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson",
        "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
        "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis",
        "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright"]

    #Generate random books
    book =[]
    current_year = datetime.now().year

    for _ in range(count):

        if random.random() < 0.7: #70% chance of book having a prefix
            title = f"{random.choice(title_prefixes)} {random.choice(title_subjects)}"
        else:
            title = random.choice(title_subjects)

        if random.random() <0.4: #40% chance of the book having a prefix
            title += f"{random.choice(title_suffixes)}"

        # Add "by Author Name" to some titles to make them more realistic
        if random.random() <0.1: #10% chance
            author = f"{random.choice(authors_first_names)} {random.choice(authors_last_names)}"
            title = f"{title} by {author}"

        #generate a random genre
        genre = random.choice(genres)

        year_weighs = [
            (1900,1950,0.1),
            (1951,2000,0.3),
            (2001,current_year, 0.6)
        ]

        #choose a weight range
        weight_choice = random.random()
        cumulative_weight = 0
        selected_range = None

        for year_start, year_end, weight in year_weighs:
            cumulative_weight += weight
            if weight_choice <= cumulative_weight:
                selected_range = (year_start, year_end)
                break

        publication_year = random.randint(selected_range[0], selected_range[1])

        # Add books to list
        books.append((title, genre, publication_year))

        # Insert books into database
    cursor.executemany("INSERT INTO books (title, genre, publication_year) VALUES (?, ?, ?)", books)
    conn.commit()
    conn.close()

    print(f"Successfully added {count} random books to the database!")
    return True

# Initializing the demo database
def init_demo_db(force_populate=False):
    """
    Initialize the demo database with sample data if it's empty or if force_populate is True.

    Args:
        force_populate: If True, will repopulate the database even if it has data
    """
    conn = sqlite3.connect(demo_db)
    cursor = conn.cursor()

    # Create table if it doesn't exist
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

    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    conn.close()

    # Populate if empty or forced
    if count == 0 or force_populate:
        return populate_demo_books(200)

    return False
