from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# PostgreSQL Configuration
DB_CONFIG = {
    "dbname": "resume_db",
    "user": "admin1",
    "password": "12345",
    "host": "localhost",
    "port": "5432"
}

# Database Connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Utility to check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Extract text from DOCX
def extract_text_from_docx(file_path):
    text = ""
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

@app.route('/parse-resumes', methods=['POST'])
def parse_resumes():
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files selected for upload"}), 400

    results = []
    conn = get_db_connection()
    cursor = conn.cursor()

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Extract text based on file type
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file_path)
            else:
                return jsonify({"error": f"Unsupported file type: {filename}"}), 400

            # Generate a unique ID
            file_id = str(uuid.uuid4())

            # Save to database
            try:
                cursor.execute(
                    """
                    INSERT INTO resumes (id, file_name, text, upload_time)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (file_id, filename, text, datetime.now())
                )
                conn.commit()
            except Exception as e:
                conn.rollback()
                return jsonify({"error": f"Database error: {str(e)}"}), 500

            # Add result for this file
            results.append({
                "id": file_id,
                "file_name": filename,
                "upload_time": datetime.now(),
                "message": "Processed successfully"
            })

            # Clean up the uploaded file
            os.remove(file_path)

    cursor.close()
    conn.close()

    return jsonify({"processed_files": results}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
