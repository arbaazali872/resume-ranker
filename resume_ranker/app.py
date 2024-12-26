from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer, util
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os
import uuid

# Initialize FastAPI app
app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "resume_db"),
    "user": os.getenv("DB_USER", "admin1"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "host": os.getenv("DB_HOST", "resume_db"),
    "port": os.getenv("DB_PORT", "5432")
}

# Initialize Sentence Transformer model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

# Pydantic models
class WebhookPayload(BaseModel):
    jd_id: str

class RankingResponse(BaseModel):
    ranked_resumes: List[dict]

# Database connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Normalize a score
def normalize_score(score, min_score, max_score):
    return (score - min_score) / (max_score - min_score) if max_score > min_score else 0

@app.post("/rank-resumes", response_model=RankingResponse)
def rank_resumes(payload: WebhookPayload):
    jd_id = payload.jd_id

    # Connect to the database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Fetch the job description
            cursor.execute("SELECT responsibilities, skills, education FROM job_descriptions WHERE id = %s", (jd_id,))
            jd_data = cursor.fetchone()

            if not jd_data:
                raise HTTPException(status_code=404, detail=f"Job description with id {jd_id} not found.")

            jd_responsibilities = jd_data["responsibilities"]
            jd_skills = jd_data["skills"]
            jd_education = jd_data["education"]

            # Fetch associated resumes
            cursor.execute("SELECT id, file_name, work_experience, skills, education FROM resumes WHERE jd_id = %s", (jd_id,))
            resumes = cursor.fetchall()

            if not resumes:
                raise HTTPException(status_code=404, detail=f"No resumes found for job description id {jd_id}.")

            # Generate embeddings for JD
            jd_responsibilities_embedding = model.encode(jd_responsibilities, convert_to_tensor=True)
            jd_skills_embedding = model.encode(jd_skills, convert_to_tensor=True)
            jd_education_embedding = model.encode(jd_education, convert_to_tensor=True)

            ranked_resumes = []

            for resume in resumes:
                # Generate embeddings for resume fields
                resume_work_embedding = model.encode(resume["work_experience"], convert_to_tensor=True)
                resume_skills_embedding = model.encode(resume["skills"], convert_to_tensor=True)
                resume_education_embedding = model.encode(resume["education"], convert_to_tensor=True)

                # Calculate similarity scores
                work_experience_score = util.pytorch_cos_sim(jd_responsibilities_embedding, resume_work_embedding).item()
                skills_score = util.pytorch_cos_sim(jd_skills_embedding, resume_skills_embedding).item()
                education_score = util.pytorch_cos_sim(jd_education_embedding, resume_education_embedding).item()

                # Normalize scores
                normalized_work_experience = normalize_score(work_experience_score, 0, 1)
                normalized_skills = normalize_score(skills_score, 0, 1)
                normalized_education = normalize_score(education_score, 0, 1)

                # Calculate universal score
                universal_score = (
                    0.5 * normalized_work_experience +
                    0.3 * normalized_skills +
                    0.2 * normalized_education
                )

                ranking_id = str(uuid.uuid4())

                # Save ranking in the database
                cursor.execute(
                    """
                    INSERT INTO rankings (id, jd_id, resume_id, work_experience_score, skills_score, education_score, universal_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        ranking_id,
                        jd_id,
                        resume["id"],
                        normalized_work_experience,
                        normalized_skills,
                        normalized_education,
                        universal_score
                    )
                )

                ranked_resumes.append({
                    "resume_id": resume["id"],
                    "file_name": resume["file_name"],
                    "work_experience_score": normalized_work_experience,
                    "skills_score": normalized_skills,
                    "education_score": normalized_education,
                    "universal_score": universal_score
                })

            conn.commit()

            # Sort resumes by universal score in descending order
            ranked_resumes.sort(key=lambda x: x["universal_score"], reverse=True)

            return {"ranked_resumes": ranked_resumes}

    except Exception as e:
        logger.error(f"Error ranking resumes for JD {jd_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while ranking resumes.")
    finally:
        conn.close()

@app.get("/get-rankings/{jd_id}")
def get_rankings(jd_id: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.resume_id, r.file_name, rk.work_experience_score, rk.skills_score, rk.education_score, rk.universal_score
                FROM resumes r
                JOIN rankings rk ON r.id = rk.resume_id
                WHERE rk.jd_id = %s
                ORDER BY rk.universal_score DESC
                """,
                (jd_id,)
            )
            rankings = cursor.fetchall()
            return {"rankings": rankings}
    except Exception as e:
        logger.error(f"Error fetching rankings for JD {jd_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching rankings.")
    finally:
        conn.close()

@app.get("/")
def root():
    return {"message": "Welcome to the Resume Ranker API!"}
