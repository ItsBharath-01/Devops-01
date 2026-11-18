# Base image: Official lightweight Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables for clean container output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set working directory inside container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and tests
COPY app.py run.py ./
COPY tests/ ./tests/

# Expose application port
EXPOSE 5000

# Start Flask application
CMD ["python", "run.py"]
