FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies first (for better caching)
# Build context is root directory, so paths are relative to root
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code to /app
COPY backend/ ./

# Copy web assets for dashboard to /web
COPY web/ /web/

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
