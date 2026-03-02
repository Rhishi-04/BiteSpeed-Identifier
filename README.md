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

- **DATABASE_URL** – SQLite by default (`sqlite:///./dev.db`). For production (e.g. Vercel) use a PostgreSQL URL (e.g. [Neon](https://neon.tech) free tier).
- **PORT** – Server port (uvicorn uses `--port`; default 8000).

---

## Deploy on Vercel

1. Push this repo to GitHub and [import it on Vercel](https://vercel.com/new).
2. Add a **PostgreSQL** database (e.g. [Neon](https://neon.tech): create a project, copy the connection string).
3. In Vercel → Project → **Settings → Environment Variables**, add:
   - **DATABASE_URL** = your Postgres connection string (e.g. `postgresql://user:pass@host/db?sslmode=require`).
4. Deploy. Your API will be at `https://<your-project>.vercel.app/identify`.

**Identify endpoint (live):** `POST https://<your-project>.vercel.app/identify` with JSON body `{"email":"...", "phoneNumber":"..."}`.
