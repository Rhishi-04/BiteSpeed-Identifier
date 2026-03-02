# Bitespeed Identify API (Python + FastAPI)

Contact identity resolution for FluxKart: link multiple emails/phones to one customer and return a consolidated view.

**Endpoint:** `POST /identify`  
**Body (JSON):** `{ "email"?: string, "phoneNumber"?: number | string }`  
**Response:** `{ "contact": { "primaryContatctId", "emails", "phoneNumbers", "secondaryContactIds" } }`

---

## Quick start

```bash
# Create virtualenv (recommended)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: copy env and set PORT/DATABASE_URL
cp .env.example .env

# Run the server
uvicorn app.main:app --reload --port 8000
```

Then:

```bash
curl -X POST http://localhost:8000/identify \
  -H "Content-Type: application/json" \
  -d '{"email":"lorraine@hillvalley.edu","phoneNumber":"123456"}'
```

---

## Project layout (familiar FastAPI structure)

| File / folder | Role |
|---------------|------|
| `app/main.py` | FastAPI app, lifespan (create DB tables), include router |
| `app/database.py` | SQLAlchemy engine, `SessionLocal`, `get_db()` dependency |
| `app/models.py` | `Contact` SQLAlchemy model (table definition) |
| `app/schemas.py` | Pydantic `IdentifyRequest`, `IdentifyResponse` |
| `app/identify_service.py` | Business logic: find/create/link contacts, build response |
| `app/routers/identify.py` | `POST /identify` route, calls service, uses `Depends(get_db)` |

---

## Environment

- **DATABASE_URL** – SQLite by default (`sqlite:///./dev.db`). For production use PostgreSQL.
- **PORT** – Server port (uvicorn uses `--port`; default 8000).

---

## Hosted endpoint

*(Add your hosted URL here after deploying, e.g. Render.)*
