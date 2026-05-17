# AI Reader — Agent guide

All user-facing strings, API responses, docs, and HTML are in **Vietnamese**.

## Run & test

```bash
pip install -r requirements.txt
cp .env.example .env   # set SECRET_KEY, JWT_SECRET_KEY (≥32 chars each)
python run.py           # starts on http://127.0.0.1:5000
pytest tests/ -v        # uses in-memory SQLite, no .env needed
```

## Architecture

- **Flask 3 app factory** (`backend/__init__.py:create_app()`)
- Entrypoint: `run.py` or `python -m backend`
- SQLite auto-created at `data/app.db` (resolved to absolute path — avoids Flask-SQLAlchemy `instance/` quirk)
- DB schema + seed data run on every startup (idempotent, `count() > 0` guard)
- `ProxyFix` middleware applied (trusts 1 proxy layer)
- Security headers set globally via `after_request`

## Auth & API quirks

- **JWT stored in HttpOnly cookies**, not Authorization header
- CSRF protection on POST/PUT/PATCH/DELETE; JS helpers auto-send `X-CSRF-TOKEN` from `csrf_access_token` cookie
- Rate limiting via Flask-Limiter (in-memory; set `RATELIMIT_STORAGE_URI` for Redis in production)
- Unauthenticated endpoints: `/health`, `/api/auth/register`, `/api/auth/login`, `/api/auth/csrf`, `/<page>.html`
- Login errors are deliberately generic: `"Email hoặc mật khẩu không đúng."`
- Password rules: ≥8 chars, 1 uppercase, 1 lowercase, 1 digit

## Frontend

- **Vanilla JS** (no framework), Tailwind CSS via CDN, Material Symbols icons
- Pages served as Flask templates from `template/` dir — allowed: `index`, `welcome`, `login`, `signup`, `home`, `timer`, `mission`, `streak`
- Route: `/` → `welcome.html`, `/<page>.html` → `template/<page>.html`

## Gamification

- Timer completion requires activating a mission first: `POST /api/user/missions/<id>/activate`
- Streaks calculated from `ReadingDay` records in `gamification_service.py`/new
- Badges, challenges, missions seeded idempotently in `seed_data.py`

## AI / Ollama

- Calls `{OLLAMA_BASE_URL}/api/chat` with system + user messages
- System prompt includes current date (seasonal recommendations)
- Response parsed by `extract_json()` — handles markdown code fences and bare JSON
- Default model: `llama3.2` (override via `OLLAMA_MODEL`)
- Prerequisite: `ollama serve` running locally

## Production checklist

- PostgreSQL instead of SQLite, Redis for rate limit storage
- `JWT_COOKIE_SECURE=true` for HTTPS
- Generate secrets via `secrets.token_hex(32)`
