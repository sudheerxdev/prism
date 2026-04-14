# Multi-stage Dockerfile for Prism/SpecFlow
# Build: docker build -t prism .
# Run:   docker run -p 3002:3002 -e OPENAI_API_KEY=sk-... prism

FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize database
RUN python -c "from queue_store import init_db; init_db()"

# Expose ports
EXPOSE 3002 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3002/_stcore/health')" || exit 1

# Default: run Streamlit UI
CMD ["python", "-m", "streamlit", "run", "app.py", \
     "--server.port=3002", \
     "--server.address=0.0.0.0", \
     "--client.toolbarMode=minimal", \
     "--logger.level=info"]
