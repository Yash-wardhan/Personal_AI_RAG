FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed for PDF parsing, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Use .env for configuration at runtime (docker-compose will provide env vars)

# Start FastAPI app with uvicorn
CMD ["fastapi", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]