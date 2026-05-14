"""
app.py — Flask backend for the Image AI Chat application
---------------------------------------------------------
Routes
  GET  /              → serve the main UI page
  POST /upload        → accept an image, generate caption, return session data
  POST /chat          → answer a follow-up question about the uploaded image
  GET  /health        → simple liveness check
"""

import os
import uuid
import base64
from io import BytesIO

from flask import Flask, request, jsonify, render_template
from PIL import Image, UnidentifiedImageError
from model import ImageAnalyzer


# ──────────────────────────────────────────────────────────
#  App configuration
# ──────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "image-ai-chat-super-secret-key-2024"  # change for production

UPLOAD_FOLDER      = "uploads"
MAX_IMAGE_BYTES    = 16 * 1024 * 1024           # 16 MB upload limit
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}

app.config["UPLOAD_FOLDER"]      = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_IMAGE_BYTES

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ──────────────────────────────────────────────────────────
#  Global AI analyzer (loaded once at startup)
# ──────────────────────────────────────────────────────────

analyzer = ImageAnalyzer()

# In-memory session store  {session_id: {...}}
# For a local single-user tool this is perfectly fine.
SESSIONS: dict = {}


# ──────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    """Return True when the filename has an accepted image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def image_to_base64(img: Image.Image) -> str:
    """Convert a PIL Image to a base-64 data-URI string (JPEG)."""
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def resize_if_needed(img: Image.Image, max_side: int = 1024) -> Image.Image:
    """
    Resize the image so neither dimension exceeds *max_side*.
    Keeps aspect ratio and only shrinks — never upscales.
    """
    w, h = img.size
    if max(w, h) > max_side:
        scale = max_side / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    return img


# ──────────────────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Render the main single-page UI."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Quick liveness probe — useful during startup."""
    return jsonify({"status": "ok", "models_loaded": analyzer.models_loaded})


@app.route("/upload", methods=["POST"])
def upload_image():
    """
    Accepts a multipart/form-data POST with field name 'image'.

    1. Validates file type.
    2. Saves to disk.
    3. Generates an image caption via BLIP.
    4. Creates a new chat session.
    5. Returns { session_id, caption, image_data, welcome_message }.
    """
    # ── Validate request ──────────────────────────────────
    if "image" not in request.files:
        return jsonify({"error": "No image field in request."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": (
                f"Unsupported file type. Please upload one of: "
                f"{', '.join(sorted(ALLOWED_EXTENSIONS)).upper()}."
            )
        }), 400

    # ── Read and validate the image ───────────────────────
    try:
        img_bytes = file.read()
        if len(img_bytes) == 0:
            return jsonify({"error": "The uploaded file is empty."}), 400

        image = Image.open(BytesIO(img_bytes)).convert("RGB")
    except UnidentifiedImageError:
        return jsonify({"error": "Could not open the file as an image. Is it corrupted?"}), 400
    except Exception as exc:
        return jsonify({"error": f"Error reading image: {exc}"}), 400

    # ── Save image to disk ────────────────────────────────
    session_id = str(uuid.uuid4())
    ext        = file.filename.rsplit(".", 1)[1].lower()
    filename   = f"{session_id}.{ext}"
    filepath   = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Resize large images before saving — faster inference, same accuracy
    image = resize_if_needed(image, max_side=1024)
    image.save(filepath, format="JPEG", quality=90)

    # ── Generate caption ──────────────────────────────────
    try:
        caption = analyzer.generate_caption(image)
    except Exception as exc:
        return jsonify({"error": f"Captioning failed: {exc}"}), 500

    # ── Build opening assistant message ───────────────────
    welcome = (
        f"I can see: **{caption}**. "
        "Feel free to ask me anything about this image!"
    )

    # ── Store session ─────────────────────────────────────
    SESSIONS[session_id] = {
        "image_path":   filepath,
        "caption":      caption,
        "conversation": [
            {"role": "assistant", "content": welcome}
        ],
    }

    return jsonify({
        "session_id":      session_id,
        "caption":         caption,
        "image_data":      image_to_base64(image),
        "welcome_message": welcome,
    })


@app.route("/chat", methods=["POST"])
def chat():
    """
    Accepts a JSON POST: { session_id, message }

    1. Validates the session and message.
    2. Runs BLIP-VQA with the stored image + user question.
    3. Appends both turns to conversation history.
    4. Returns { response, conversation }.
    """
    data       = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "").strip()
    user_msg   = data.get("message", "").strip()

    # ── Validate ──────────────────────────────────────────
    if not session_id:
        return jsonify({"error": "Missing session_id."}), 400

    if session_id not in SESSIONS:
        return jsonify({"error": "Session not found. Please upload an image first."}), 404

    if not user_msg:
        return jsonify({"error": "Message cannot be empty."}), 400

    if len(user_msg) > 500:
        return jsonify({"error": "Message too long (max 500 characters)."}), 400

    session = SESSIONS[session_id]

    # ── Load image from disk ──────────────────────────────
    try:
        image = Image.open(session["image_path"]).convert("RGB")
    except Exception as exc:
        return jsonify({"error": f"Could not reload image: {exc}"}), 500

    # ── Run VQA ───────────────────────────────────────────
    try:
        raw_answer = analyzer.answer_question(image, user_msg)
    except Exception as exc:
        return jsonify({"error": f"Inference error: {exc}"}), 500

    # ── Polish response ───────────────────────────────────
    response = analyzer.build_response(raw_answer, user_msg, session["caption"])

    # ── Update conversation history ───────────────────────
    session["conversation"].append({"role": "user",      "content": user_msg})
    session["conversation"].append({"role": "assistant", "content": response})

    return jsonify({
        "response":     response,
        "conversation": session["conversation"],
    })


# ──────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Image AI Chat — Local Server")
    print("=" * 60)
    print("\n[startup] Loading AI models …")
    print("          (First run downloads ~900 MB — please wait)\n")

    analyzer.load_models()

    print("\n[startup] ✓ Models ready.")
    print("[startup] ✓ Opening server at http://127.0.0.1:5000\n")
    print("  Open your browser and go to:  http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop the server.\n")
    print("=" * 60)

    # debug=False keeps things stable; threaded=False avoids race conditions
    # with the global in-memory session dict.
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=False)
