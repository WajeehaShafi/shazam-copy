import sqlite3

DB_PATH = "shazam.db"


def get_connection():
    """Create/connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_tables():
    """Create the songs and fingerprints tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fingerprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            time_offset INTEGER NOT NULL,
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
    """)

    # Index on hash makes lookups during matching MUCH faster
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints (hash)
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")


def add_song(title, artist=""):
    """Insert a new song and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO songs (title, artist) VALUES (?, ?)", (title, artist))
    song_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return song_id


def store_fingerprints(song_id, hashes):
    """
    Store a list of (hash, time_offset) tuples for a given song.
    Uses executemany for speed — this could be 400k+ rows per song.
    """
    conn = get_connection()
    cursor = conn.cursor()
    data = [(h, song_id, int(t)) for h, t in hashes]
    cursor.executemany(
        "INSERT INTO fingerprints (hash, song_id, time_offset) VALUES (?, ?, ?)",
        data
    )
    conn.commit()
    conn.close()
    print(f"Stored {len(data)} fingerprints for song_id={song_id}")


if __name__ == "__main__":
    create_tables()