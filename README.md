# Resume Ranking System

![Resume Ranking System Banner](path/to/banner-image.png)

## Description

The **Resume Ranking System** is a modular tool designed to automate and streamline the recruitment process. It parses resumes and job descriptions (JDs), calculates semantic similarities, and ranks candidates based on their suitability for the job. By leveraging state-of-the-art technologies, this system simplifies candidate evaluation for recruiters.

---

## Features

- **Upload Functionality:**Interface for uploading resumes and job descriptions.
- **Semantic Similarity Scoring:** Leverages NLP models to compare resumes with JDs effectively.
- **Automated Ranking:** Generates rankings based on predefined weighted criteria (work experience, skills, and education).
- **Intuitive Results Display:** Provides ranking results for recruiters.

---

## Technologies Used

- **Programming Languages:** Python
- **Frameworks and Libraries:**
  - **Frontend:** Django
  - **Backend:** Flask, FastAPI
  - **NLP:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Database:** PostgreSQL
- **Deployment:** Docker and Docker Compose

---


## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository:**
   ```bash
   git clone git@github.com:arbaazali872/resume-ranker.git
   cd resume-ranking-system
2. **Set Up Docker Environment:**

 Ensure Docker and Docker Compose are installed on your machine.Then, run the following command to build and start the services:

```bash
docker-compose up --build
```

## Access the Application

Once the services are up and running, you can access them through the following URLs:

- **Frontend:** [http://localhost:8001](http://localhost:8001)
- **Resume Ranker API:** [http://localhost:8000](http://localhost:8000)
- **Resume Parser API:** [http://localhost:5000](http://localhost:5000)


## Configuration

### Environment Variables

Add a `.env` file in the root directory with the following keys:

```makefile
DB_NAME=resume_db
DB_USER=admin
DB_PASSWORD=12345
DB_HOST=resume_db
DB_PORT=5432
```


## Testing

To test individual services, follow the steps below:

1. **Resume Frontend:**  
   - Upload resumes and JDs through the web interface and validate the displayed results.

2. **Resume Parser:**  
   - Send a `POST` request with resumes and JDs to the following endpoint:  
     ```http
     POST http://localhost:5000/upload-jd-resumes
     ```

3. **Resume Ranker:**  
   - Verify rankings by querying the endpoint:  
     ```http
     GET http://localhost:8000/get-rankings/{jd_id}
     ```
