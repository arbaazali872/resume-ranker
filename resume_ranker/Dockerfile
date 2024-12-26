# Use Python 3.9 slim image as the base
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install the dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the application code into the container
COPY . /app

# Expose the port on which the service will run
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
