FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY models /app/models
COPY tasks /app/tasks
COPY sockets /app/sockets

ENV PYTHONPATH=/app

EXPOSE 5000

CMD ["python", "backend/app.py"]