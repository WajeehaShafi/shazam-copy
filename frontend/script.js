const BACKEND_URL = "http://127.0.0.1:8000/match";
const CHUNK_DURATION_MS = 5000; // 5 seconds per rolling chunk

const listenBtn = document.getElementById("listenBtn");
const statusEl = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const resultTitle = document.getElementById("resultTitle");
const resultArtist = document.getElementById("resultArtist");
const resultScore = document.getElementById("resultScore");

let isListening = false;
let mediaStream = null;
let mediaRecorder = null;

listenBtn.addEventListener("click", () => {
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
});

async function startListening() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
        statusEl.textContent = "Microphone access denied.";
        return;
    }

    isListening = true;
    listenBtn.classList.add("listening");
    resultCard.classList.add("hidden");
    statusEl.textContent = "Listening...";

    recordChunkLoop();
}

function stopListening() {
    isListening = false;
    listenBtn.classList.remove("listening");
    statusEl.textContent = "Tap to start listening";

    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
    }
    if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
    }
}

function recordChunkLoop() {
    if (!isListening) return;

    const chunks = [];
    mediaRecorder = new MediaRecorder(mediaStream);

    mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        await sendChunkToServer(blob);

        // If still listening (no confident match yet), record the next chunk
        if (isListening) {
            recordChunkLoop();
        }
    };

    mediaRecorder.start();
    setTimeout(() => {
        if (mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
    }, CHUNK_DURATION_MS);
}

async function sendChunkToServer(blob) {
    const formData = new FormData();
    formData.append("file", blob, "chunk.webm");

    try {
        const response = await fetch(BACKEND_URL, {
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (data.match) {
            showResult(data);
            stopListening();
        } else {
            statusEl.textContent = "Listening... no match yet";
        }
    } catch (err) {
        statusEl.textContent = "Error contacting server.";
        console.error(err);
    }
}

function showResult(data) {
    resultTitle.textContent = data.title;
    resultArtist.textContent = data.artist || "Unknown Artist";
    resultScore.textContent = `Confidence score: ${data.score}`;
    resultCard.classList.remove("hidden");
    statusEl.textContent = "Match found!";
}