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
