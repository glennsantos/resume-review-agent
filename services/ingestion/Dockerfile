FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src

# Set PYTHONPATH so Uvicorn can locate the ingestion package
ENV PYTHONPATH=/app/src

# Expose port and run
EXPOSE 8000
CMD ["uvicorn", "ingestion.main:app", "--host", "0.0.0.0", "--port", "8000"]
