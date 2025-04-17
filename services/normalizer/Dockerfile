FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src

# Set PYTHONPATH so the normalizer package is discoverable
ENV PYTHONPATH=/app/src

# Run the normalizer subscriber
CMD ["python3", "normalizer/main.py"]
