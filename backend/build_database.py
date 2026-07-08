import os
from fingerprint import fingerprint_file
from database import add_song, store_fingerprints, create_tables, get_connection

SONGS_FOLDER = "songs"

ARTIST_MAP = {
    "Heavyweight": "Gurinder Gill, Jazzy B",
    "Boom Shaka": "KR$NA, Dhanda Nyol",
    "Badd Bunnyy": "Rawal, Agsy",
    "Jhoot": "Bibash Jk, Talha Anjum",
    "Jo Mei Hun": "Emiway Bantai",
    "Old Monk": "Baby Jean",
    "Toh Phir Aao": "Mustafa Zahid",
    "Tumhi Din Chadhe Tumhi Din Dhale": "Kavita Sheth, Neeraj",
    "Vallah": "Bayanni, Harrdy Sandhu",
    "Yung Money": "Afusic, Ali Raza",
}


def song_already_exists(title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM songs WHERE title = ?", (title,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def build_database():
    create_tables()

    for filename in os.listdir(SONGS_FOLDER):
        if filename.lower().endswith((".mp3", ".wav")):
            filepath = os.path.join(SONGS_FOLDER, filename)
            title = os.path.splitext(filename)[0]

            if song_already_exists(title):
                print(f"Skipping (already in DB): {title}")
                continue

            artist = ARTIST_MAP.get(title, "Unknown Artist")

            print(f"Processing: {title} by {artist}")
            hashes = fingerprint_file(filepath)
            song_id = add_song(title=title, artist=artist)
            store_fingerprints(song_id, hashes)
            print(f"Done: {title} -> {len(hashes)} hashes stored\n")


if __name__ == "__main__":
    build_database()