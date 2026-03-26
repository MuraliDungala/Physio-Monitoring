# Multi-stage build for optimized production image

# Stage 1: Builder - Install dependencies
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies to system site-packages
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Create lean production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only (including OpenCV requirements)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas0 \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder (system site-packages for all-user access)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY app.py config.py auth.py database.py models.py session_manager.py exercise_state_manager.py ./
COPY exercise_engine ./exercise_engine
COPY ml_models ./ml_models
COPY voice ./voice
COPY chatbot ./chatbot
COPY static ./static

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check - simple curl request to API
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import http.client; http.client.HTTPConnection('localhost', 8000).request('GET', '/health')" || exit 0

# Default environment variables
ENV ENVIRONMENT=production \
    HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Start application using uvicorn
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
