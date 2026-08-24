# Tera Projekt Interior Architecture Management Platform

A premium FastAPI management platform for an interior architecture, interior decoration and project-delivery company. It includes executive analytics, People & Culture, architecture/design workflows, project portfolio control, client briefs, FF&E/material specifications, site inspections, snagging, procurement, CRM, finance, payroll, timesheets, invoices, documents, approvals, risks and audit logs.

## Deploy the demo

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mbquashie/TeraProjekt)

The included `render.yaml` provisions the Python web service and a PostgreSQL database. The application seeds its demo dataset automatically on first start.

## Core team seeded
- Elsie Amedzi — HR Manager
- Ethel Amedzi — Lead Architect
- Kojo Yankson — Senior Architect
- Jerry Dwansah — Project Architect

The demo dataset contains 48 employees across Architecture & Design, Interior Design, Project Delivery, Visualization, Quantity Surveying, Procurement/FF&E, Finance & Administration, Commercial, Client Experience, People & Culture, and Operations.

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

## Security note
The repository intentionally excludes `.env`, local SQLite databases, uploads, cache files and other runtime data. Change all demo passwords and secrets before real production use. For production, use PostgreSQL, HTTPS, secure cookies, managed secrets, backups, durable object storage for uploads, and a proper identity provider.
