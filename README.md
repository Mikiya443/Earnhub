# Earnhubs Full Stack

A full-stack Earnhubs starter built with:

- Django + Django REST Framework: core API, authentication, wallet, tasks, referrals, withdrawals, admin
- Node.js + Socket.IO: realtime events/notifications
- React + Vite: responsive web frontend
- SQLite by default for easy local development

## Architecture

React -> Django REST API
React -> Node Socket.IO for realtime updates
Django -> database/business rules
Node -> realtime gateway

## Run Django

```bash
cd django_backend
python -m venv .venv
# Linux/Termux:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Django API: http://localhost:8000/api/
Django admin: http://localhost:8000/admin/

## Run Node

In another terminal:

```bash
cd realtime
npm install
cp .env.example .env
npm start
```

Realtime server: http://localhost:3001

## Run React

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: http://localhost:5173

## Production notes

This project is a strong development foundation. Before real-money production use, add a real payment provider with verified webhooks, idempotency, reconciliation, KYC/AML controls where required, audit logs, backups, monitoring, HTTPS, secure secrets, and a production database such as PostgreSQL.

## Render deployment

This version includes `render.yaml` for a Django service, Node realtime service, React static site, and PostgreSQL database. See `RENDER_DEPLOY.md`.
