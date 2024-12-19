FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Install only Chromium browser
RUN playwright install chromium
RUN playwright install-deps chromium

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the Lambda function
CMD ["python", "lambda_function.py"] 