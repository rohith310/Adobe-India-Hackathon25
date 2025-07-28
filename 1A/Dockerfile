# Use Python 3.11 for better PyMuPDF compatibility
FROM python:3.11-slim

# Install system dependencies that PyMuPDF might need
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all Python source files
COPY *.py ./

# Create input and output directories
RUN mkdir -p input output

# Command to run the application
ENTRYPOINT ["python", "main.py"]
