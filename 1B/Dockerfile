# Use Python 3.11 for better PyMuPDF compatibility
FROM python:3.11-slim

# Install system dependencies for PyMuPDF and ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY utils.py .

# Create directories
RUN mkdir -p input output models

# Set environment variables for CPU-only execution
ENV TOKENIZERS_PARALLELISM=false
ENV OMP_NUM_THREADS=1

# Set entrypoint
ENTRYPOINT ["python", "main.py"]
