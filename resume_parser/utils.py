import PyPDF2
from docx import Document
import spacy

# Load SpaCy model globally
nlp = spacy.load("en_core_web_sm")


ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    text = ""
    doc = Document(file_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def extract_skills(text):
    """Custom logic to extract skills."""
    skills_keywords = ["Python", "Java", "Machine Learning", "NLP", "Data Science"]
    skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
    return ", ".join(skills)

def extract_education(text):
    """Custom logic to extract education."""
    education_keywords = ["Bachelor", "Master", "PhD", "Degree", "Diploma"]
    education = []
    for line in text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in education_keywords):
            education.append(line.strip())
    return ", ".join(education)

def extract_work_experience(text):
    """Custom logic to extract work experience."""
    work_keywords = ["Experience", "Worked", "Job", "Position", "Role"]
    experience = []
    for line in text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in work_keywords):
            experience.append(line.strip())
    return ", ".join(experience)

def extract_structured_info(text):
    """
    Extract structured information from resume text using SpaCy.
    """
    doc = nlp(text)
    
    # Example: Extract named entities
    entities = {
        "PERSON": [],
        "ORG": [],
        "DATE": [],
        "GPE": [],
    }
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    # Extract specific sections
    skills = extract_skills(text)
    education = extract_education(text)
    work_experience = extract_work_experience(text)
    personal_projects = extract_personal_projects(text)
    print(f"""

    skills: {skills}

    education: {education}

    work_experience: {work_experience}

    personal_projects: {personal_projects}

""")

    return {
        "skills": skills,
        "education": education,
        "work_experience": work_experience,
        "personal_projects": personal_projects,
        "entities": entities
    }

def extract_personal_projects(text):
    """Custom logic to extract personal projects."""
    project_keywords = ["Project", "Built", "Developed", "Designed", "Created"]
    projects = []
    is_project_section = False

    for line in text.split("\n"):
        if "personal project" in line.lower():
            is_project_section = True
        elif is_project_section and any(keyword.lower() in line.lower() for keyword in project_keywords):
            projects.append(line.strip())
        elif is_project_section and line.strip() == "":  # Exit on empty line
            break

    return ", ".join(projects)
