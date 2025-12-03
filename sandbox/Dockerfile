FROM python:3.14-slim

WORKDIR /app

# Install system dependencies for Playwright and Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

COPY . .

CMD ["python", "analyzer.py"]
