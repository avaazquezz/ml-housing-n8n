FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better Docker layer caching
COPY requirements.txt requirements-test.txt ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install test dependencies (only if requirements-test.txt exists)
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy application code
COPY . .

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
