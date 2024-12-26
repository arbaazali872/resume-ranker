import re

def extract_jd_sections(jd_text):
    """
    Extract structured sections from a job description.

    Args:
        jd_text (str): The raw text of the job description.

    Returns:
        dict: A dictionary containing responsibilities, education, and skills.
    """
    # Initialize dictionary to store extracted sections
    jd_sections = {
        "responsibilities": "",
        "education": "",
        "skills": ""
    }

    # Define section headers and synonyms
    section_mapping = {
        "responsibilities": ["key responsibilities", "responsibilities", "role overview","what you will do","Your Responsibilities"],
        # "education": ["education", "requirements", "qualifications"],
        "education": ["education"],
        "skills": ["skills", "skills & experience", "preferred qualifications", "tools and platforms","who you are", "Your profile","requirements", "qualifications"]
    }

    # Compile regex to detect section headers
    header_regex = re.compile(
        r"^({})[:\n\t ]*$".format("|".join(
            header for synonyms in section_mapping.values() for header in synonyms
        )),
        re.IGNORECASE
    )

    # Initialize variables for parsing
    current_section = None
    for line in jd_text.splitlines():
        line = line.strip()

        # Check if the line matches any section header
        if header_regex.match(line):
            for section, synonyms in section_mapping.items():
                if any(header in line.lower() for header in synonyms):
                    current_section = section
                    break
        elif current_section:
            jd_sections[current_section] += line + " "

    # Clean up extracted sections
    for section in jd_sections:
        jd_sections[section] = jd_sections[section].strip()

    return jd_sections
