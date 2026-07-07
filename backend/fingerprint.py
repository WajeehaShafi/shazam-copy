import numpy as np
import librosa
from scipy.ndimage import maximum_filter
from scipy.ndimage import binary_erosion
import hashlib

# ---- CONFIG ----
SAMPLE_RATE = 22050
N_FFT = 4096
HOP_LENGTH = 512
PEAK_NEIGHBORHOOD_SIZE = 20   # how "sparse" peaks should be
FAN_VALUE = 15                # how many pairs to make per peak
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200


def load_audio(file_path):
    """Load audio file and convert to mono waveform."""
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
    return y, sr


def create_spectrogram(y):
    """Convert waveform to a magnitude spectrogram (time-frequency representation)."""
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    return S_db  # shape: (freq_bins, time_frames)


def find_peaks(S_db):
    """
    Find local maxima ('peaks') in the spectrogram.
    These are the loudest, most distinctive points — Shazam's key trick
    is that peaks survive noise/compression better than raw audio does.
    """
    struct = np.ones((PEAK_NEIGHBORHOOD_SIZE, PEAK_NEIGHBORHOOD_SIZE))
    local_max = maximum_filter(S_db, footprint=struct) == S_db

    # remove background (very quiet) points from counting as peaks
    background = (S_db == np.min(S_db))
    eroded_background = binary_erosion(background, structure=struct, border_value=1)
    detected_peaks = local_max & ~eroded_background

    freq_idx, time_idx = np.where(detected_peaks)
    peaks = list(zip(freq_idx, time_idx))
    return peaks


def generate_hashes(peaks):
    """
    Pair up nearby peaks and hash them.
    A hash = (freq1, freq2, time_delta) -> this combination is
    far more unique and noise-resistant than a single peak alone.
    """
    peaks.sort(key=lambda x: x[1])  # sort by time
    hashes = []

    for i in range(len(peaks)):
        for j in range(1, FAN_VALUE):
            if (i + j) < len(peaks):
                freq1, t1 = peaks[i]
                freq2, t2 = peaks[i + j]
                t_delta = t2 - t1

                if MIN_HASH_TIME_DELTA <= t_delta <= MAX_HASH_TIME_DELTA:
                    # Create a hash string and hash it
                    hash_input = f"{freq1}|{freq2}|{t_delta}"
                    h = hashlib.sha1(hash_input.encode()).hexdigest()[:20]
                    hashes.append((h, t1))  # (hash, time_offset)

    return hashes


def fingerprint_file(file_path):
    """Full pipeline: file -> hashes."""
    y, sr = load_audio(file_path)
    S_db = create_spectrogram(y)
    peaks = find_peaks(S_db)
    hashes = generate_hashes(peaks)
    return hashes


if __name__ == "__main__":
    # quick test
    test_file = "songs/Heavyweight Gurinder Gill (pagalall.com).mp3"
    hashes = fingerprint_file(test_file)
    print(f"Generated {len(hashes)} hashes")
    print("Sample hashes:", hashes[:5])