# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Install SpaCy model
# RUN python -m spacy download en_core_web_sm
# Copy the application code into the container
COPY . .

# Expose the port that Flask runs on
EXPOSE 5000

# Set environment variables to avoid buffering logs
ENV PYTHONUNBUFFERED=1

# Run the Flask application
CMD ["python", "app.py"]
