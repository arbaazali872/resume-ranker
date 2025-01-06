import requests
import uuid
from django.shortcuts import render, redirect
from .forms import JobDescriptionForm, ResumeForm

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


import requests
from django.shortcuts import render
from django.http import Http404
import logging

# Logging setup
logger = logging.getLogger(__name__)

def rank_results(request, jd_id):
    try:
        # Step 1: Construct the URL for the resume ranking service
        url = f'http://resume_ranker:8000/get-rankings/{jd_id}'

        # Step 2: Make the GET request to the resume_ranker service
        response = requests.get(url)

        # Step 3: Handle unsuccessful requests
        if response.status_code != 200:
            logger.error(f"Failed to fetch rankings for JD ID {jd_id}: {response.status_code}")
            raise Http404("Ranking data not found.")
        
        # Step 4: Get the ranking data from the response
        rankings = response.json().get("ranked_resumes", [])

        print("got the rankings from parser: ",rankings )

        # Step 5: Render the results in the template
        return render(request, 'resume_handler/rank_results.html', {'rankings': rankings})

    except requests.exceptions.RequestException as e:
        logger.error(f"Error during API call to Resume Ranker: {str(e)}")
        raise Http404("Error fetching rankings data.")

