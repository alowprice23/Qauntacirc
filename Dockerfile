# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency definition files
COPY pyproject.toml .
COPY version.py .

# Install dependencies
# We install setuptools and wheel first to ensure pyproject.toml can be handled
RUN pip install --no-cache-dir setuptools wheel
RUN pip install --no-cache-dir -e .

# Copy the rest of the application's source code from the host to the container
COPY . .

# The CMD will be specified in the docker-compose.yml for each service
# For example: CMD ["python", "run_orchestrator.py"]