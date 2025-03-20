"""
This module provides a Flask Blueprint for analyzing PDF files.

It includes functionality to:
- Validate uploaded PDF files.
- Extract text content from PDF files using PyMuPDF (fitz).
- Analyze the extracted text using the OpenAI-based analysis client.

Routes:
    - POST /analyze: Accepts PDF files, extracts text, and returns the
                     analysis results.

Modules Imported:

- os: For file and directory management.
- fitz: For PDF text extraction.
- flask: For creating the API endpoints and handling requests.
- werkzeug.utils: For securing filenames.
- ai_logic.openai_client: For analyzing extracted text.
"""
import os
import fitz
from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename
from ai_logic.openai_client import analyze_text

analyze_bp = Blueprint("analyze", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """
    Check if a given filename has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        (bool): True if the file has a valid extension (PDF), False otherwise.
    """
    has_extension = "." in filename
    extension = filename.rsplit(".", 1)[1].lower()

    return has_extension and extension in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file: str) -> str | None:
    """
    Extract text content from a PDF file.

    Args:
        file (str): The PDF file to extract text from.

    Returns:
        (str | None): Extracted text as a single string if successful, o
                    None if extraction fails.
    """
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(pdf_path)

    with fitz.open(pdf_path) as doc:
        text = "\n".join([page.get_text() for page in doc])

    return text.strip() if text else None


@analyze_bp.route("/analyze", methods=["POST"])
def analyze() -> tuple[Response, int] | Response:
    """
    Analyze the content of a PDF by extracting its text and performing analysis.

    This endpoint accepts PDF files, extracts their text content, and sends it
    to the analysis function.

    Returns:
        (tuple[Response, int] | Response): JSON response with analysis results
                                         if successful, or an error message
                                         with a 400 status code if an issue
                                         occurs.
    """
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
