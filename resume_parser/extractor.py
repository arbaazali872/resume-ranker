import re

def extract_relevant_sections(resume_text):
    """
    Extracts only the relevant sections: skills, education, work experience, and personal projects.

    Args:
        resume_text (str): The raw text of the resume.

    Returns:
        dict: A dictionary containing the four sections with their respective content.
    """
    # Initialize dictionary to store relevant sections
    relevant_sections = {
        "skills": "",
        "education": "",
        "work_experience": "",
        "personal_projects": ""
    }

    # Define relevant section headers and synonyms
    section_mapping = {
        "skills": ["skills", "technical skills"],
        "education": ["education"],
        "work_experience": ["work experience", "experience"],
        "personal_projects": ["personal projects", "projects"]
    }

    # Compile regex to detect section headers
    header_regex = re.compile(
        r"^({})[:\n\t ]*$".format("|".join(
            header for synonyms in section_mapping.values() for header in synonyms
        )),
        re.IGNORECASE
    )

    current_section = None
    for line in resume_text.splitlines():
        line = line.strip()

        # Check if the line matches any relevant section header
        if header_regex.match(line):
            for section, synonyms in section_mapping.items():
                if line.lower() in synonyms:
                    current_section = section
                    break
        elif current_section:
            relevant_sections[current_section] += line + "\n"

    # Clean up the extracted sections (strip trailing newlines and whitespace)
    for section in relevant_sections:
        relevant_sections[section] = relevant_sections[section].strip()
        print(f"""
          
we are inside extractor2:
          
          {relevant_sections}
          
          """)
    return relevant_sections

# # Example usage
# if __name__ == "__main__":
#     # Simulate loading a resume file (replace with actual resume text loading)
#     resume_text = """
#     EDUCATION
#     Masters in Data Science and Artificial Intelligence
#     University of Trento, Italy / École Centrale de Nantes, France
#     September 2023 – Continued
#     Recipient of the EIT Manufacturing Scholarship

#     WORK EXPERIENCE
#     MaqsoodLabs (maqsoodlabs.com)  Lahore, Pakistan
#     AI Engineer | Python Developer  2022-2023
#     News-watcher: Developed a Python script for web scraping to download and parse news articles...
#     News-clustering : Developed and Deployed a script utilizing NLP Techniques...

#     PERSONAL PROJECTS
#     Resume Ranking WebApp: Developed a Dockerized Resume Ranking WebApp leveraging NLP techniques...
#     InsightRetriever Chatbot: Developed InsightRetriever, a news research chatbot tool...

#     SKILLS
#     Data Skills: LLM, NLP, Data Processing, Python, PostgreSQL, BigQuery...
#     Development Technologies: Docker, REST API, GIT, CI/CD...
#     """

#     # Run the extraction
#     relevant_sections = extract_relevant_sections(resume_text)

#     # Print the results
#     for section, content in relevant_sections.items():
#         print(f"--- {section.upper()} ---")
#         print(content)
#         print()
