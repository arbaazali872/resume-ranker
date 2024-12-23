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
        r"^({})[:\\n\\t ]*$".format("|".join(
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

    return relevant_sections
