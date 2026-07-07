from collections import defaultdict, Counter
from fingerprint import fingerprint_file
from database import get_connection


def match_clip(clip_path):
    print(f"Fingerprinting clip: {clip_path}")
    clip_hashes = fingerprint_file(clip_path)  # [(hash, time_offset), ...]
    print(f"Clip produced {len(clip_hashes)} hashes")

    conn = get_connection()
    cursor = conn.cursor()

    # song_id -> Counter of (db_time - clip_time) offsets
    matches_per_song = defaultdict(Counter)

    for h, clip_time in clip_hashes:
        cursor.execute(
            "SELECT song_id, time_offset FROM fingerprints WHERE hash = ?",
            (h,)
        )
        rows = cursor.fetchall()

        for song_id, db_time in rows:
            delta = db_time - clip_time
            matches_per_song[song_id][delta] += 1

    conn.close()

    if not matches_per_song:
        print("No matches found at all.")
        return None

    # For each song, find its best-aligned offset and how many hashes agree on it
    best_song_id = None
    best_score = 0
    best_offset = 0

    for song_id, offset_counts in matches_per_song.items():
        offset, count = offset_counts.most_common(1)[0]
        if count > best_score:
            best_score = count
            best_song_id = song_id
            best_offset = offset

    # Look up song title
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, artist FROM songs WHERE id = ?", (best_song_id,))
    title, artist = cursor.fetchone()
    conn.close()

    print(f"\nBest match: {title} by {artist}")
    print(f"Aligned hash matches: {best_score} (at offset {best_offset})")

    return {"title": title, "artist": artist, "score": best_score}


if __name__ == "__main__":
    test_clip = "test_clip.mp3"
    match_clip(test_clip)