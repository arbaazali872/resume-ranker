import requests
import uuid
from django.shortcuts import render, redirect
from .forms import JobDescriptionForm, ResumeForm
import psycopg2
import requests
from django.shortcuts import render
from django.http import Http404
from django.shortcuts import render
import os
import logging

# Logging setup
logger = logging.getLogger(__name__)

# Endpoint configuration for the resume_parser service
RESUME_PARSER_ENDPOINT = "http://resume_parser:5000/upload-jd-resumes"
GET_RANKINGS_ENDPOINT = "http://resume_ranker:8000/get-rankings/{jd_id}"

def handle_uploads(request):
    if request.method == 'POST':
        jd_form = JobDescriptionForm(request.POST, request.FILES)
        resume_form = ResumeForm(request.POST, request.FILES)

        if jd_form.is_valid() and resume_form.is_valid():
            jd_file = jd_form.cleaned_data['job_description']
            resumes = request.FILES.getlist('files')

            # Prepare files for the API
            files = {
                'jd': (jd_file.name, jd_file.file)
            }

            # Add each resume as a separate file entry
            for i, resume in enumerate(resumes):
                files[f'resume_{i}'] = (resume.name, resume.file)

            try:
                # Send files to the resume_parser service
                response = requests.post(RESUME_PARSER_ENDPOINT, files=files)
                response.raise_for_status()

                # Get the JD ID from the response
                jd_data = response.json()
                jd_id = jd_data.get("jd", {}).get("jd_id")

                if not jd_id:
                    raise ValueError("JD ID not found in the response.")

                # Redirect to rankings page
                return redirect('rank_results', jd_id=jd_id)

            except requests.exceptions.RequestException as e:
                # Log the error and show a message to the user
                print(f"Error while uploading files: {str(e)}")
                return render(request, 'resume_handler/handle_uploads1.html', {
                    'jd_form': jd_form,
                    'resume_form': resume_form,
                    'error': "Failed to upload files. Please try again."
                })

        else:
            # Render the form with errors
            return render(request, 'resume_handler/handle_uploads1.html', {
                'jd_form': jd_form,
                'resume_form': resume_form,
                'error': "Invalid form submission. Please fix the errors."
            })

    # Render the initial form
    return render(request, 'resume_handler/handle_uploads1.html', {
        'jd_form': JobDescriptionForm(),
        'resume_form': ResumeForm()
    })





# Database configuration sourced from environment variables
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "resume_db"),
    "user": os.getenv("DB_USER", "admin1"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "host": os.getenv("DB_HOST", "resume_db"),
    "port": os.getenv("DB_PORT", "5432")
}

def get_db_connection():
    """Establish a connection to the PostgreSQL database with error handling."""
    try:
        conn = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        return conn

    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        return None  # Return None to indicate failure

    except Exception as e:
        logger.error(f"Unexpected error while connecting to the database: {e}")
        return None


def rank_results(request, jd_id):
    """Retrieve and display rankings from the database based on JD ID."""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to establish a database connection.")
        raise Http404("Database connection error. Please try again later.")
    try:
        with conn.cursor() as cursor:
            # Fetch rankings from the database
            cursor.execute(
                """
                SELECT resume_id, resume_file_name, work_experience_score, skills_score, education_score, universal_score
                FROM rankings
                WHERE jd_id = %s
                ORDER BY universal_score DESC
                """,
                (jd_id,)
            )
            rankings = cursor.fetchall()

            if not rankings:
                logger.warning(f"No rankings found for JD ID {jd_id}")
                raise Http404("No rankings available for this job description.")

            # Transform database results into a format suitable for the template
            formatted_rankings = [
                {
                    "resume_id": row[0],
                    "file_name": row[1],
                    "work_experience_score": row[2],
                    "skills_score": row[3],
                    "education_score": row[4],
                    "universal_score": row[5]
                }
                for row in rankings
            ]

            # Render the results in the template
            return render(request, 'resume_handler/rank_results.html', {'rankings': formatted_rankings})

    except Exception as e:
        logger.error(f"Error fetching rankings for JD ID {jd_id}: {str(e)}")
        raise Http404("An error occurred while fetching rankings.")

    finally:
        conn.close()


# def rank_results(request, jd_id):
#     try:
#         # Step 1: Construct the URL for the resume ranking service
#         url = f'http://resume_ranker:8000/get-rankings/{jd_id}'

#         # Step 2: Make the GET request to the resume_ranker service
#         response = requests.get(url)

#         # Step 3: Handle unsuccessful requests
#         if response.status_code != 200:
#             logger.error(f"Failed to fetch rankings for JD ID {jd_id}: {response.status_code}")
#             raise Http404("Ranking data not found.")
        
#         # Step 4: Transform the ranking data for template rendering
#         rankings = [
#             {
#                 "resume_id": row["resume_id"],
#                 "file_name": row["resume_file_name"],
#                 "work_experience_score": row["work_experience_score"],
#                 "skills_score": row["skills_score"],
#                 "education_score": row["education_score"],
#                 "universal_score": row["universal_score"]
#             }
#             for row in response.json()["rankings"]
#         ]

#         # Step 5: Render the results in the template
#         return render(request, 'resume_handler/rank_results.html', {'rankings': rankings})

#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error during API call to Resume Ranker: {str(e)}")
#         raise Http404("Error fetching rankings data.")
