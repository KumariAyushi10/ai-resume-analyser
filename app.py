import os
import uuid
from flask import Flask, request, jsonify, render_template

from resume_parser import extract_text, ParseError
from ats_analyzer import analyze_resume
from llm_integration import get_llm_suggestions, llm_available

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html", llm_available=llm_available())


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file was uploaded."}), 400

    file = request.files["resume"]
    jd_text = request.form.get("job_description", "").strip()
    use_llm = request.form.get("use_llm") == "true"

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Please upload a PDF, DOCX, or TXT file."}), 400

    temp_name = f"{uuid.uuid4().hex}_{file.filename}"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_name)
    file.save(temp_path)

    try:
        resume_text = extract_text(temp_path)
        result = analyze_resume(resume_text, jd_text)

        if use_llm and llm_available():
            llm_suggestions = get_llm_suggestions(resume_text, jd_text, result)
            if llm_suggestions:
                result["llm_suggestions"] = llm_suggestions

        result["llm_available"] = llm_available()
        return jsonify(result)

    except ParseError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Something went wrong while analyzing the resume: {e}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
