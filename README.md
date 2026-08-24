# Tera Projekt Interior Architecture Management Platform

A premium FastAPI management platform for an interior architecture, interior decoration and project-delivery company. It includes executive analytics, People & Culture, architecture/design workflows, project portfolio control, client briefs, FF&E/material specifications, site inspections, snagging, procurement, CRM, finance, payroll, timesheets, invoices, documents, approvals, risks and audit logs.

## Core team seeded
- Elsie Amedzi — HR Manager
- Ethel Amedzi — Lead Architect
- Kojo Yankson — Senior Architect
- Jerry Dwansah — Project Architect

The demo dataset contains a broader multi-disciplinary Tera Projekt team across Architecture & Design, Interior Design, Project Delivery, Visualization, Quantity Surveying, Procurement/FF&E, Finance & Administration, Commercial, Client Experience, People & Culture, and Operations.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Open http://localhost:8000

## Demo accounts
Password for all demo users: `Tera2026!`
- admin@teraprojekt.com — Administrator
- elsie@teraprojekt.com — HR Manager
- ethel@teraprojekt.com — Project Manager / Lead Architect
- kojo@teraprojekt.com — Project Manager / Senior Architect
- jerry@teraprojekt.com — Project Manager / Project Architect
- nanaama@teraprojekt.com — Finance Manager
- adjoa@teraprojekt.com — Employee

## Demo deployment
This repository includes `render.yaml` for a Render web-service + PostgreSQL deployment. Set a strong `SECRET_KEY`, keep `COOKIE_SECURE=1`, and use the managed PostgreSQL `DATABASE_URL` supplied by the hosting platform.

## Security note
The repository intentionally excludes `.env`, local SQLite databases, uploads, cache files and other runtime data. Change all demo passwords and secrets before real production use. For production, use PostgreSQL, HTTPS, secure cookies, managed secrets, backups, and a proper identity provider.
