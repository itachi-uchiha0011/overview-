# Overview

A soft, lovable productivity + community platform — Notion meets Discord.

## Stack
- Frontend: React + Vite + Tailwind CSS
- Backend: Flask, SQLAlchemy, Flask-SocketIO
- DB: PostgreSQL
- Realtime: Socket.IO
- Queue: Celery + Redis
- Auth: JWT

## Quickstart (Docker)
1. Copy `.env.example` to `.env` and adjust values.
2. Run: `docker-compose up --build`
3. Backend API: http://localhost:5000/api/health
4. Frontend: http://localhost:5173

## Quickstart (Local)
- Services: install PostgreSQL and Redis locally
- Create DB `overview` with user `overview:overview`
- Python:
  ```bash
  python3.11 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  export FLASK_ENV=development
  python backend/app.py
  ```
- Celery:
  ```bash
  celery -A tasks.celery_app.celery_app worker -l info
  ```
