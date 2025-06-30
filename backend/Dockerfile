FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Debug: List the files to see what's actually copied
RUN echo "=== Files in /app ===" && ls -la /app
RUN echo "=== Files in /app/models ===" && ls -la /app/models || echo "models directory not found"
RUN echo "=== Python path ===" && python -c "import sys; print(sys.path)"

# Expose port (adjust as needed)
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"]