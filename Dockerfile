FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# These are common container settings.

# The second one is particularly useful because application logs appear immediately in the container output rather than being unnecessarily buffered.

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
# This documents that the application listens on port 8000.
# It does not, by itself, make the port accessible from Windows. We'll handle that when we run the container.

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
