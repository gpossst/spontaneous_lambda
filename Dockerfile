FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install only Chromium browser
RUN playwright install chromium
RUN playwright install-deps chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Verify installations
RUN pip list

# Run the FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]