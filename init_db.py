import sqlite3
from config import Config

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(Config.DATABASE_URL)
    c = conn.cursor()
    
    # Create the vibe table
    c.execute('''
        CREATE TABLE IF NOT EXISTS vibe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            github_url TEXT,
            summary TEXT,
            description TEXT,
            click_count INTEGER DEFAULT 0,
            stars_count INTEGER DEFAULT 0,
            json TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 