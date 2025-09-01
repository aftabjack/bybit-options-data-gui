FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from parent directory
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy webapp files
COPY webapp/ .

# Create a non-root user
RUN useradd -m -u 1000 webapp && chown -R webapp:webapp /app
USER webapp

# Expose the web port
EXPOSE 5001

CMD ["python", "-u", "app_fastapi.py"]