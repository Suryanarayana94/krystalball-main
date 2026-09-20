# KristalBar Inventory Forecasting System

A hotel bar inventory forecasting and dynamic par-level recommendation system designed for multi-property inventory operations.

## Overview

This project is a production-oriented prototype for managing bar inventory using historical consumption, forecasting, safety stock, and inventory simulation. The solution is modular enough to support real CSV data, demo data, and future automation.

## Stack

- Frontend: React + Vite
- Backend: FastAPI + Pydantic
- Data layer: pandas + numpy
- Database: PostgreSQL-ready models and schema layout
- Testing: pytest

## Folder structure

- `frontend/` — React dashboard
- `backend/` — FastAPI backend and logic
- `data/` — raw and processed datasets
- `reports/` — outputs and summaries
- `notebooks/` — analysis notebooks

## Backend setup

```powershell
cd C:\Users\Admin\OneDrive\Desktop\kristalball
backend\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Frontend setup

```powershell
cd C:\Users\Admin\OneDrive\Desktop\kristalball\frontend
npm install
npm run dev -- --host 0.0.0.0
```

## API routes

- GET `/api/health`
- GET `/api/dashboard/summary`
- GET `/api/inventory`
- GET `/api/brands`
- GET `/api/bars`
- GET `/api/forecast`
- GET `/api/recommendations`
- GET `/api/analytics/abc`
- GET `/api/data-quality`
- GET `/api/model-performance`
- GET `/api/consumption`
- GET `/api/ready`

## Demo data

The project includes realistic demo data for development and demo workflows. It is clearly separated from production data assumptions and is intended for local evaluation only.

## Testing

```powershell
cd C:\Users\Admin\OneDrive\Desktop\kristalball
backend\.venv\Scripts\python -m pytest backend/tests/test_inventory_core.py -q
```

## Notes

This is a working baseline for the hotel bar forecasting system. It is intentionally modular so the demo data layer can be replaced by real transaction ingestion and a Postgres-backed operational model.
