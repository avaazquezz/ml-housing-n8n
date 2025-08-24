FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

# Copy requirements first for better Docker layer caching
COPY requirements.txt requirements-test.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install test dependencies (only if requirements-test.txt exists)
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy application code
COPY . .

# Create model directory and set permissions
RUN mkdir -p /app/model && \
    chown -R app:app /app

# Switch to app user
USER app

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
