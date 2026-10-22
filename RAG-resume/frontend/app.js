
/* =========================================================
   RAG Document Assistant — Frontend Logic

   Responsibilities:
   1. Select PDF/TXT files.
   2. Validate files.
   3. Support drag and drop.
   4. Upload files to the Flask backend.
   5. Display chat messages and retrieved evidence.
   6. Send questions to the RAG pipeline.
   ========================================================= */

// ---------- 1. Configuration ----------

// Flask will serve the frontend and API from the same origin.
// Therefore, we can use relative API paths.
const API_UPLOAD_URL = "/api/upload";
const API_ASK_URL = "/api/ask";

// Maximum file size: 10 MB.
const MAX_FILE_SIZE = 10 * 1024 * 1024;


// ---------- 2. Get HTML elements ----------

const fileInput = document.getElementById("file-input");
const uploadBox = document.getElementById("upload-box");
const fileCard = document.getElementById("file-card");
const fileIcon = document.getElementById("file-icon");
const fileName = document.getElementById("file-name");
const fileMeta = document.getElementById("file-meta");

const removeFileButton = document.getElementById("remove-file-button");
const uploadButton = document.getElementById("upload-button");
const uploadMessage = document.getElementById("upload-message");

const chatWindow = document.getElementById("chat-window");
const welcomeMessage = document.getElementById("welcome-message");
const questionForm = document.getElementById("question-form");
const questionInput = document.getElementById("question-input");
const sendButton = document.getElementById("send-button");
const evidenceContainer = document.getElementById("evidence-container");


// ---------- 3. Application state ----------

// The currently selected file.
let selectedFile = null;

// True only after the backend successfully processes the document.
let documentProcessed = false;

// Prevent multiple simultaneous requests.
let isUploading = false;
let isAsking = false;


// ---------- 4. File validation ----------

function validateFile(file) {
    if (!file) {
        return "Please select a file.";
    }

    const extension = file.name.split(".").pop().toLowerCase();

    if (!["pdf", "txt"].includes(extension)) {
        return "Unsupported file type. Please select a PDF or TXT file.";
    }

    if (file.size === 0) {
        return "The selected file is empty.";
    }

    if (file.size > MAX_FILE_SIZE) {
        return "The file is too large. Please select a file under 10 MB.";
    }

    return null;
}


// ---------- 5. Display status messages ----------

function showUploadMessage(message, type = "info") {
    uploadMessage.textContent = message;

    // These classes can be styled in CSS.
    uploadMessage.classList.remove(
        "status-success",
        "status-error",
        "status-info"
    );

    uploadMessage.classList.add(`status-${type}`);
}


// ---------- 6. Enable or disable chat ----------

function setChatEnabled(enabled) {
    questionInput.disabled = !enabled;
    sendButton.disabled = !enabled;
}


// ---------- 7. Select and display a file ----------

function selectFile(file) {
    const error = validateFile(file);

    if (error) {
        selectedFile = null;
        documentProcessed = false;

        fileInput.value = "";
        fileCard.hidden = true;
        uploadButton.disabled = true;
        setChatEnabled(false);

        showUploadMessage(error, "error");
        return;
    }

    selectedFile = file;
    documentProcessed = false;

    const extension = file.name.split(".").pop().toLowerCase();

    fileIcon.textContent = extension === "pdf" ? "📄" : "📝";
    fileName.textContent = file.name;
    fileMeta.textContent = `${formatFileSize(file.size)} • ${extension.toUpperCase()} file`;

    fileCard.hidden = false;
    uploadButton.disabled = false;

    setChatEnabled(false);
    evidenceContainer.replaceChildren();

    showUploadMessage(
        "File selected. Click “Process document” to prepare it for questions.",
        "info"
    );
}


// ---------- 8. Format file size ----------

function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}


// ---------- 9. Reset the selected document ----------

function resetDocument() {
    selectedFile = null;
    documentProcessed = false;

    fileInput.value = "";
    fileCard.hidden = true;
    uploadButton.disabled = true;

    questionInput.value = "";
    setChatEnabled(false);

    evidenceContainer.replaceChildren();

    showUploadMessage("Choose a PDF or TXT file to get started.", "info");
}


// ---------- 10. Upload and process the document ----------

async function uploadDocument() {
    if (!selectedFile || isUploading) {
        return;
    }

    const error = validateFile(selectedFile);

    if (error) {
        showUploadMessage(error, "error");
        return;
    }

    isUploading = true;
    uploadButton.disabled = true;
    uploadButton.textContent = "Processing...";
    setChatEnabled(false);

    showUploadMessage(
        "Uploading and processing your document. This may take a little while...",
        "info"
    );

    try {
        // FormData sends the file as multipart/form-data.
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(API_UPLOAD_URL, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "The document could not be processed.");
        }

        documentProcessed = true;
        setChatEnabled(true);

        showUploadMessage(
            `${data.message || "Document processed successfully."} ` +
            `${data.chunk_count ?? "?"} chunks are ready for retrieval.`,
            "success"
        );

        // Keep the response available for future UI improvements.
        console.log("Document processing result:", data);

    } catch (error) {
        console.error("Upload error:", error);

        showUploadMessage(
            error.message ||
            "Could not connect to the backend. Check that Flask is running.",
            "error"
        );

    } finally {
        isUploading = false;
        uploadButton.textContent = "Process document";
        uploadButton.disabled = !selectedFile;
    }
}


// ---------- 11. Add a chat message safely ----------

function addChatMessage(text, sender) {
    const message = document.createElement("div");

    message.classList.add(
        "chat-message",
        sender === "user" ? "user-message" : "assistant-message"
    );

    const label = document.createElement("div");
    label.classList.add("message-label");
    label.textContent = sender === "user" ? "You" : "RAG Assistant";

    const content = document.createElement("div");
    content.classList.add("message-content");

    // textContent treats uploaded content and model output as plain text.
    // This avoids interpreting them as HTML.
    content.textContent = text;

    message.append(label, content);

    if (welcomeMessage) {
        welcomeMessage.hidden = true;
    }

    chatWindow.appendChild(message);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    return message;
}


// ---------- 12. Display retrieved evidence ----------

function displayEvidence(chunks) {
    evidenceContainer.replaceChildren();

    if (!Array.isArray(chunks) || chunks.length === 0) {
        return;
    }

    const heading = document.createElement("h3");
    heading.classList.add("evidence-heading");
    heading.textContent = "Retrieved evidence";
    evidenceContainer.appendChild(heading);

    chunks.forEach((chunk, index) => {
        const card = document.createElement("article");
        card.classList.add("evidence-card");

        const header = document.createElement("div");
        header.classList.add("evidence-header");

        const title = document.createElement("span");
        title.classList.add("evidence-title");
        title.textContent = chunk.chunk_id || `Evidence ${index + 1}`;

        const score = document.createElement("span");
        score.classList.add("evidence-score");

        const similarity = Number(chunk.similarity_score);

        score.textContent = Number.isFinite(similarity)
            ? `Similarity: ${similarity.toFixed(3)}`
            : "Similarity unavailable";

        const content = document.createElement("p");
        content.classList.add("evidence-text");
        content.textContent = chunk.text || "No evidence text returned.";

        header.append(title, score);
        card.append(header, content);
        evidenceContainer.appendChild(card);
    });
}


// ---------- 13. Ask a question ----------

async function askQuestion(question) {
    if (!documentProcessed || isAsking) {
        return;
    }

    const cleanedQuestion = question.trim();

    if (!cleanedQuestion) {
        return;
    }

    isAsking = true;
    sendButton.disabled = true;
    questionInput.disabled = true;

    addChatMessage(cleanedQuestion, "user");

    const loadingMessage = addChatMessage(
        "Searching your document and generating an answer...",
        "assistant"
    );

    try {
        const response = await fetch(API_ASK_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: cleanedQuestion
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not answer this question.");
        }

        // Replace the loading message with the actual answer.
        loadingMessage.querySelector(".message-content").textContent =
            data.answer || "The backend returned no answer.";

        displayEvidence(data.retrieved_chunks);

    } catch (error) {
        console.error("Question error:", error);

        loadingMessage.querySelector(".message-content").textContent =
            `Error: ${error.message || "Could not connect to the backend."}`;

    } finally {
        isAsking = false;
        questionInput.disabled = !documentProcessed;
        sendButton.disabled = !documentProcessed;
        questionInput.focus();
    }
}


// ---------- 14. Connect UI events ----------

// File chosen using the file picker.
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (file) {
        selectFile(file);
    }
});

// Remove selected file.
removeFileButton.addEventListener("click", resetDocument);

// Send selected file to Flask.
uploadButton.addEventListener("click", uploadDocument);

// Drag and drop support.
uploadBox.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadBox.classList.add("drag-over");
});

uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-over");
});

uploadBox.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadBox.classList.remove("drag-over");

    const file = event.dataTransfer.files[0];

    if (file) {
        // Assigning to fileInput.files isn't needed for upload;
        // selectFile stores the file in application state.
        selectFile(file);
    }
});

// Submit a question.
questionForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const question = questionInput.value;
    if (!question.trim()) {
        return;
    }

    questionInput.value = "";
    askQuestion(question);
});

// Enter sends; Shift+Enter adds a newline.
questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        questionForm.requestSubmit();
    }
});


// ---------- 15. Initial UI state ----------

setChatEnabled(false);
uploadButton.disabled = true;
fileCard.hidden = true;

showUploadMessage(
    "Choose a PDF or TXT file to get started.",
    "info"
);

console.log("RAG Document Assistant frontend initialized.");
