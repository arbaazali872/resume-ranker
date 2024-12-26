import re

def extract_relevant_sections(resume_text):
    """
    Extracts sections: skills, education, work experience, and personal projects from a resume.

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

    # Define section headers and their synonyms
    section_mapping = {
        "skills": ["skills", "technical skills", "professional skills"],
        "education": ["education", "academic", "qualifications","certifications"],
        "work_experience": ["work experience", "experience", "employment"],
        "personal_projects": ["personal projects", "projects", "portfolio"]
    }

    # Compile regex to detect section headers
    header_regex = re.compile(
        r"^\s*({})\s*[:\n\t ]*$".format("|".join(
            header for synonyms in section_mapping.values() for header in synonyms
        )),
        re.IGNORECASE
    )

    # Keep track of the current section
    current_section = None
    bullet_regex = re.compile(r"^[-●•]\s*")  # Regex to detect bullet points

    # Split the resume into lines for processing
    for line in resume_text.splitlines():
        line = line.strip()

        # Check if the line matches any relevant section header
        if header_regex.match(line):
            for section, synonyms in section_mapping.items():
                if any(line.lower().startswith(header.lower()) for header in synonyms):
                    current_section = section
                    break
        elif current_section:
            # Append line to the current section
            if bullet_regex.match(line):  # Handle bullet points
                relevant_sections[current_section] += "\n- " + bullet_regex.sub("", line)
            else:
                relevant_sections[current_section] += " " + line

    # Clean up extracted sections
    for section in relevant_sections:
        relevant_sections[section] = re.sub(r"\s+", " ", relevant_sections[section]).strip()
        print(f"""
        Debugging Extractor:
        Current Section: {section.upper()}
        Content: {relevant_sections[section]}
        """)

    return relevant_sections

# Example usage
if __name__ == "__main__":
    # Simulate loading a resume file (replace with actual resume text loading)
    resume_text = """
    ARBAAZ ALI Trento, Italy | https://www.linkedin.com/in/engineerarbaaz/ | +33 7 68 18 39 82 | arbaazali872@gmail.com | https://arbaazali872.github.io/ EDUCATION Masters in Data Science and Artificial Intelligence September 2023 – Continued University of Trento, Italy / École Centrale de Nantes, France Recipient of the EIT Manufacturing Scholarship, awarded for academic excellence and potential in innovation for the manufacturing industry. WORK EXPERIENCE: MaqsoodLabs (maqsoodlabs.com) Lahore, Pakistan AI Engineer | Python Developer 2022-2023 ● News-watcher: Developed a Python-based web scraping tool to collect and analyze news articles, extracting key insights stored in PostgreSQL for trend analysis and reporting. ● News-clustering: Implemented an NLP solution using the BERT model to group similar articles based on shared topics, improving the efficiency of data analysis and insight generation. Deployed the solution using Docker for consistent performance across different systems. ● Fashion Recommender: Designed a recommendation system utilizing Ximilar API and Doc2Vec to generate product suggestions. Deployed the system on a Django website and managed real-time updates with AWS cron jobs, enhancing customer engagement through personalized product recommendations. PERSONAL PROJECTS: Tableau: Analysis of the Impact of Price Variations: Conducted an Exploratory Data Analysis (EDA) to assess how pricing changes affect sales performance. Applied forecasting techniques and developed a comprehensive Tableau dashboard to present actionable insights. View project. Power BI: BikeShare Business Analysis: Designed and implemented an end-to-end Power BI dashboard for a bike-sharing company, providing key insights into revenue trends, rider demographics, and pricing strategies. Used SQL to integrate data and generate robust reporting structures. SKILLS: • Data Skills: LLM, NLP, Data Processing, Python, PostgreSQL, BigQuery, Data ETL Pipelines, SMOTE, Imbalanced Data handling, Keras DAX • Data Analysis and Visualization: Streamlit, Tableau, Power BI, Excel, SQL • Project Management: Agile Project Management • Behavioral skills: Leadership, Analytical Thinking, Time management, Flexibility and Adaptability, Effective communication. • Development Technologies: Docker, REST API, GIT, CI/CD, GCP Vertex AI, AWS EC2 CERTIFICATIONS • GOOGLE CLOUD BIG DATA AND MACHINE LEARNING FUNDAMENTALS 2024 • ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING 2021-2022 • MICROSOFT-CERTIFIED AZURE AI FUNDAMENTALS (AI-900) 2021 LANGUAGES • English (Fluent), French (Intermediate)    """

    # Run the extraction
    relevant_sections = extract_relevant_sections(resume_text)

    # Print the results
    for section, content in relevant_sections.items():
        print(f"--- {section.upper()} ---")
        print(content)
        print()
