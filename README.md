# 🎵 Shazam Clone

A web-based song identification system built with a client-server architecture. Play any song near your microphone, and the app identifies the track by matching audio "fingerprints" against a pre-built database — the same core technique used by the real Shazam app.

---

## How It Works

Instead of comparing raw audio, the app breaks each song down into a **spectrogram** (a time-vs-frequency picture of the audio), extracts the loudest/most distinct points (**peaks**), and pairs nearby peaks into unique **hashes**. These hashes are noise-resistant and survive background noise, re-encoding, and partial clips.

To identify a clip:
1. The clip is fingerprinted using the same process as the songs in the database.
2. Each hash from the clip is looked up in the database.
3. For every match, the time offset between the clip and the original song is calculated.
4. If a clip truly belongs to a song, a large number of matches will cluster around the **same offset** — this cluster size becomes the confidence score.
5. The song with the strongest, most consistent offset cluster is returned as the match.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (Web Audio API / MediaRecorder) |
| Backend | Python, FastAPI |
| Audio Processing | NumPy, SciPy, Librosa |
| Database | SQLite |
| Containerization | Docker, Docker Compose |

---

## Project Structure

```
shazam-clone/
├── backend/
│   ├── fingerprint.py      # Spectrogram generation, peak detection, hashing
│   ├── database.py         # SQLite table creation and data access
│   ├── build_database.py   # Fingerprints all songs in songs/ and stores them
│   ├── match.py            # Matches a clip against the database
│   ├── main.py              # FastAPI server exposing /match endpoint
│   ├── songs/                # Source mp3 files
│   ├── shazam.db             # SQLite database (auto-generated)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Running Locally (without Docker)

### 1. Install backend dependencies
```bash
cd backend
pip install fastapi uvicorn python-multipart pydub numpy scipy librosa matplotlib
```
> Requires `ffmpeg` installed and available on your system PATH (used for audio decoding).

### 2. Build the song database
Add `.mp3` files to `backend/songs/`, then run:
```bash
python build_database.py
```
This fingerprints every song and stores the results in `shazam.db`.

### 3. Start the backend server
```bash
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000`. API docs available at `http://127.0.0.1:8000/docs`.

### 4. Serve the frontend
In a separate terminal:
```bash
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500` in your browser.

### 5. Use the app
Click the mic button, allow microphone access, and play a song near your device. The app records rolling 5-second audio chunks and checks each one against the database until a confident match is found.

---

## Running with Docker

From the project root:
```bash
docker compose up --build
```

This builds and starts two containers:
- **shazam-backend** → FastAPI server at `http://localhost:8000`
- **shazam-frontend** → Static site served via nginx at `http://localhost:5500`

Open `http://localhost:5500` in your browser and use the app exactly as described above — no local Python or dependency installation required.

To stop the containers:
```bash
docker compose down
```

---

## API Reference

### `POST /match`
Accepts an audio file upload and returns the best matching song.

**Request:** `multipart/form-data` with a `file` field containing an audio clip.

**Response:**
```json
{
  "match": true,
  "title": "Boom Shaka",
  "artist": "KR$NA, Dhanda Nyol",
  "score": 13506
}
```
- `match`: `true` if the confidence score meets the threshold, otherwise `false`.
- `score`: number of fingerprint hashes that aligned at the same time offset — higher means a stronger match.

### `GET /`
Health check endpoint. Returns:
```json
{"status": "Shazam clone backend running"}
```

---

## Current Song Library

The database currently contains 10 songs, each identified by title and artist, fingerprinted and indexed for fast lookup via SQLite.

---

## Notes

- Audio matching accuracy improves with clearer, louder audio input and reduced background noise.
- The matching confidence threshold is configurable in `main.py` (`CONFIDENCE_THRESHOLD`).
- Song files and the generated `shazam.db` are excluded from version control via `.gitignore`; run `build_database.py` locally (or via Docker) to regenerate the database from the songs in `backend/songs/`.