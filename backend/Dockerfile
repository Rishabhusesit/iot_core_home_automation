FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ .

EXPOSE 5000

# Start Flask app
CMD ["python", "app.py"]
