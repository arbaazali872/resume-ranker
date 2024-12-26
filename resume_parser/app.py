from flask import Flask, request, jsonify
import os
import uuid
from datetime import datetime
from utils import allowed_file, extract_text_from_pdf, extract_text_from_docx
from resume_extractor import extract_relevant_sections
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from jd_parser import extract_jd_sections
# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "resume_db"),
    "user": os.getenv("DB_USER", "admin1"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "host": os.getenv("DB_HOST", "resume_db"),
    "port": os.getenv("DB_PORT", "5432")
}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Function to process job descriptions
def process_job_description(jd_file, jd_id):
    """Process the JD file and save it to the database with extracted sections."""
    if not allowed_file(jd_file.filename):
        return {"error": f"Unsupported file type for JD: {jd_file.filename}"}

    jd_filename = os.path.join(app.config['UPLOAD_FOLDER'], jd_file.filename)
    jd_file.save(jd_filename)

    # Extract JD text
    try:
        jd_text = (
            extract_text_from_pdf(jd_filename) if jd_filename.endswith('.pdf')
            else extract_text_from_docx(jd_filename)
        )
    except Exception as e:
        print(f"Error extracting text from JD: {str(e)}")
        return {"error": f"Text extraction error for JD: {jd_file.filename}"}
    finally:
        os.remove(jd_filename)

    # Extract structured information
    structured_jd = extract_jd_sections(jd_text)
    print(f"Extracted structured JD: {structured_jd}")

    # Save JD to database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO job_descriptions (id, file_name, text, responsibilities, education, skills, upload_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    jd_id,
                    jd_file.filename,
                    jd_text,
                    structured_jd.get("responsibilities", ""),
                    structured_jd.get("education", ""),
                    structured_jd.get("skills", ""),
                    datetime.now()
                )
            )
            conn.commit()
            print(f"JD {jd_file.filename} processed successfully.")
        return {"jd_id": jd_id, "file_name": jd_file.filename, "message": "JD processed successfully","structured_jd":structured_jd}
    except Exception as e:
        conn.rollback()
        print(f"Database error while saving JD: {str(e)}")
        return {"error": f"Database error for JD: {str(e)}"}
    finally:
        conn.close()


# Function to process resumes
def process_resumes(resume_files, jd_id):
    results = []
    conn = get_db_connection()

    for resume_file in resume_files:
        if not allowed_file(resume_file.filename):
            logger.warning(f"Skipping unsupported file: {resume_file.filename}")
            results.append({"file_name": resume_file.filename, "message": "Unsupported file type"})
            continue

        resume_filename = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
        resume_file.save(resume_filename)

        try:
            # Extract text
            resume_text = (
                extract_text_from_pdf(resume_filename) if resume_filename.endswith('.pdf')
                else extract_text_from_docx(resume_filename)
            )

            # Extract structured information
            structured_info = extract_relevant_sections(resume_text)
            structured_info = {key: structured_info.get(key, "") for key in ["skills", "education", "work_experience", "personal_projects"]}

            resume_id = str(uuid.uuid4())

            # Insert into database
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO resumes (id, jd_id, file_name, text, skills, education, work_experience, personal_projects, upload_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        resume_id,
                        jd_id,
                        resume_file.filename,
                        resume_text,
                        structured_info["skills"],
                        structured_info["education"],
                        structured_info["work_experience"],
                        structured_info["personal_projects"],
                        datetime.now()
                    )
                )
                conn.commit()
                logger.info(f"Resume {resume_file.filename} processed successfully.")
                results.append({
                    "file_name": resume_file.filename,
                    "structured_info": structured_info,
                    "message": "Processed successfully"
                })

        except Exception as e:
            conn.rollback()
            logger.error(f"Error processing resume {resume_file.filename}: {str(e)}")
            results.append({
                "file_name": resume_file.filename,
                "message": f"Failed to process: {str(e)}"
            })
        finally:
            os.remove(resume_filename)

    conn.close()
    return results

@app.route('/upload-jd-resumes', methods=['POST'])
def upload_jd_resumes():
    if 'jd' not in request.files or 'resumes' not in request.files:
        return jsonify({"error": "JD or resumes not provided"}), 400

    jd_file = request.files['jd']
    resume_files = request.files.getlist('resumes')
    jd_id = str(uuid.uuid4())

    jd_result = process_job_description(jd_file, jd_id)
    if "error" in jd_result:
        return jsonify(jd_result), 500

    resumes_result = process_resumes(resume_files, jd_id)
    return jsonify({"jd": jd_result, "resumes": resumes_result}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
