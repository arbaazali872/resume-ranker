-- Table for storing job descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY,                -- Unique ID for each JD
    file_name VARCHAR(255) NOT NULL,    -- JD file name
    text TEXT NOT NULL,                 -- Raw JD text
    responsibilities TEXT,              -- Extracted responsibilities
    education TEXT,                     -- Extracted education
    skills TEXT,                        -- Extracted skills
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Upload timestamp
);

-- Table for storing resumes
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY,                -- Unique ID for each resume
    jd_id UUID NOT NULL,                -- Reference to the associated job description
    file_name VARCHAR(255) NOT NULL,    -- Resume file name
    text TEXT NOT NULL,                 -- Raw resume text
    skills TEXT,                        -- Extracted skills
    education TEXT,                     -- Extracted education
    work_experience TEXT,               -- Extracted work experience
    personal_projects TEXT,             -- Extracted personal projects
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jd_id) REFERENCES job_descriptions (id) -- Reference JD table
);

CREATE TABLE IF NOT EXISTS rankings (
    id UUID PRIMARY KEY,              -- Unique ID for each ranking
    jd_id UUID NOT NULL,              -- Reference to the job description
    resume_id UUID NOT NULL,          -- Reference to the resume
    resume_file_name VARCHAR(255),    -- Reference to the resume
    work_experience_score REAL,       -- Normalized work experience score
    skills_score REAL,                -- Normalized skills score
    education_score REAL,             -- Normalized education score
    universal_score REAL,             -- Final ranking score
    ranking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp for ranking
    FOREIGN KEY (jd_id) REFERENCES job_descriptions (id),
    FOREIGN KEY (resume_id) REFERENCES resumes (id)
);
