# NutriScan AI

A beginner-friendly FastAPI + SQLite + SQLAlchemy project. It uses RapidFuzz to compare user-entered ingredients with health-condition risk rules, calculates a safety score, suggests substitutions, and stores every analysis in SQLite.

## Windows setup

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create the virtual environment:

```powershell
python -m venv venv
```

4. Activate it:

```powershell
venv\Scripts\activate
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
```

5. Install dependencies:

```powershell
pip install -r requirements.txt
```

6. Start the app:

```powershell
python main.py
```

The application automatically creates/updates the SQLite tables and health rules.

7. Open:

`http://127.0.0.1:8000`

FastAPI docs:

`http://127.0.0.1:8000/docs`

## Quick test

Select **Celiac / Gluten Intolerance**, enter:

```text
Wheat Flour, Sugar, Salt, Palm Oil
```

and click **Analyze Safety Risks**.

You should see wheat flagged and a suggested substitution. You can also select multiple conditions.

## API endpoints

- `GET /` — dashboard
- `GET /api/conditions` — health conditions stored in the database
- `POST /api/analyze` — analyze ingredients and save result
- `GET /api/history` — return saved analyses

## Architecture

```text
Browser (HTML/CSS/JavaScript)
          ↓
       FastAPI
          ↓
      SQLAlchemy
          ↓
       SQLite
```

RapidFuzz is used in the backend for conservative typo matching.
