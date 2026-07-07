import os
from fingerprint import fingerprint_file
from database import add_song, store_fingerprints, create_tables, get_connection

SONGS_FOLDER = "songs"


def song_already_exists(title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM songs WHERE title = ?", (title,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def build_database():
    create_tables()  # ensure tables exist

    for filename in os.listdir(SONGS_FOLDER):
        if filename.lower().endswith((".mp3", ".wav")):
            filepath = os.path.join(SONGS_FOLDER, filename)
            title = os.path.splitext(filename)[0]

            if song_already_exists(title):
                print(f"Skipping (already in DB): {title}")
                continue

            print(f"Processing: {title}")
            hashes = fingerprint_file(filepath)
            song_id = add_song(title=title, artist="Unknown")
            store_fingerprints(song_id, hashes)
            print(f"Done: {title} -> {len(hashes)} hashes stored\n")


if __name__ == "__main__":
    build_database()