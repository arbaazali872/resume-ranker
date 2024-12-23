from flask import Flask, request, jsonify
import os
import uuid
from datetime import datetime
from utils import allowed_file, extract_text_from_pdf, extract_text_from_docx
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# PostgreSQL Configuration
DB_CONFIG = {
    "dbname": "resume_db",
    "user": "admin1",
    "password": "12345",
    "host": "resume_db",
    "port": "5432"
}

# Database connection
def get_db_connection():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Function to process and save a job description
def process_job_description(jd_file, jd_id, upload_folder):
    """Process the JD file and save it to the database."""
    if not allowed_file(jd_file.filename):
        return {"error": "Unsupported JD file type"}

    jd_filename = os.path.join(upload_folder, jd_file.filename)
    jd_file.save(jd_filename)

    # Extract JD text
    jd_text = (
        extract_text_from_pdf(jd_filename) if jd_filename.endswith('.pdf')
        else extract_text_from_docx(jd_filename)
    )

    # Save JD to database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO job_descriptions (id, file_name, text, upload_time)
            VALUES (%s, %s, %s, %s)
            """,
            (jd_id, jd_file.filename, jd_text, datetime.now())
        )
        conn.commit()
        return {"jd_id": jd_id, "file_name": jd_file.filename, "message": "JD processed successfully"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Database error while saving JD: {str(e)}"}
    finally:
        cursor.close()
        conn.close()
        os.remove(jd_filename)  # Clean up JD file

# Function to process and save resumes
def process_resumes(resume_files, jd_id, upload_folder):
    """Process the resume files and save them to the database."""
    results = []
    conn = get_db_connection()
    cursor = conn.cursor()

    for resume_file in resume_files:
        if not allowed_file(resume_file.filename):
            results.append({"file_name": resume_file.filename, "message": "Unsupported file type"})
            continue

        resume_filename = os.path.join(upload_folder, resume_file.filename)
        resume_file.save(resume_filename)

        # Extract resume text
        resume_text = (
            extract_text_from_pdf(resume_filename) if resume_filename.endswith('.pdf')
            else extract_text_from_docx(resume_filename)
        )

        try:
            cursor.execute(
                """
                INSERT INTO resumes (id, file_name, text, upload_time)
                VALUES (%s, %s, %s, %s)
                """,
                (jd_id, resume_file.filename, resume_text, datetime.now())
            )
            conn.commit()
            results.append({
                "file_name": resume_file.filename,
                "message": "Processed successfully"
            })
        except Exception as e:
            conn.rollback()
            results.append({
                "file_name": resume_file.filename,
                "message": f"Failed to process: {str(e)}"
            })
        finally:
            os.remove(resume_filename)  # Clean up resume file

    cursor.close()
    conn.close()
    return results

@app.route('/upload-jd-resumes', methods=['POST'])
def upload_jd_resumes():
    """Handle JD and resume uploads."""
    if 'jd' not in request.files or 'resumes' not in request.files:
        return jsonify({"error": "JD or resumes not provided"}), 400

    jd_file = request.files['jd']
    resume_files = request.files.getlist('resumes')

    # Generate a shared UUID
    jd_id = str(uuid.uuid4())

    # Process JD
    jd_result = process_job_description(jd_file, jd_id, app.config['UPLOAD_FOLDER'])

    if jd_result.get("error"):
        return jsonify(jd_result), 500

    # Process resumes
    resumes_result = process_resumes(resume_files, jd_id, app.config['UPLOAD_FOLDER'])

    return jsonify({"jd": jd_result, "resumes": resumes_result}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
