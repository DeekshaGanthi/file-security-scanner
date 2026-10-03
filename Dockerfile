FROM python:3.12-slim

WORKDIR /app

# Install Linux dependencies required by yara-python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libyara-dev \
    yara \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend ./backend
COPY frontend ./frontend

# Create runtime directory used for uploaded files
RUN mkdir -p /app/uploads

EXPOSE 8000 8501

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]