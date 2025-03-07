import os
import fitz
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ai_logic.openai_client import analyze_text

analyze_bp = Blueprint("analyze", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file):
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(pdf_path)

    with fitz.open(pdf_path) as doc:
        text = "\n".join([page.get_text() for page in doc])

    return text.strip() if text else None

@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    extracted_text = extract_text_from_pdf(file)

    if not extracted_text:
        return jsonify({"error": "Could not extract text from PDF"}), 400

    result = analyze_text(extracted_text)

    return jsonify(result)

