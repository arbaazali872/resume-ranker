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
        "responsibilities": ["key responsibilities", "responsibilities", "role overview", "what you will do", "your responsibilities"],
        "education": ["education", "requirements", "qualifications"],
        "skills": ["skills", "skills & experience", "preferred qualifications", "tools and platforms", "who you are", "your profile", "requirements", "qualifications"]
    }

    # Define irrelevant section headers to drop
    irrelevant_headers = [
        "how to apply", "about us", "what we offer", "preferred qualifications"
    ]

    # Compile regex to detect relevant and irrelevant section headers
    relevant_header_regex = re.compile(
        r"^({})[:\n\t ]*$".format("|".join(
            header for synonyms in section_mapping.values() for header in synonyms
        )),
        re.IGNORECASE
    )

    irrelevant_header_regex = re.compile(
        r"^({})[:\n\t ]*$".format("|".join(irrelevant_headers)),
        re.IGNORECASE
    )

    # Initialize variables for parsing
    current_section = None
    for line in jd_text.splitlines():
        line = line.strip()

        # Check if the line matches any irrelevant section header
        if irrelevant_header_regex.match(line):
            current_section = None  # Skip irrelevant sections
            continue

        # Check if the line matches any relevant section header
        if relevant_header_regex.match(line):
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
