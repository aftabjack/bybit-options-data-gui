FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY options_tracker_production.py .

# Create a non-root user
RUN useradd -m -u 1000 tracker && chown -R tracker:tracker /app
USER tracker

# Health check endpoint will be on port 8080
EXPOSE 8080

CMD ["python", "-u", "options_tracker_production.py"]