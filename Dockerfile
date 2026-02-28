# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for pdfplumber/pdfminer (if any) and general build tools
RUN apt-get update && apt-get install -y --no-install-recommends 
    gcc 
    && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the application and its dependencies
RUN pip install --no-cache-dir .

# Create a directory for mounting volumes
RUN mkdir -p /data
WORKDIR /data

# Set the entrypoint to the CLI tool
ENTRYPOINT ["distill"]

# Default command shows help
CMD ["--help"]
