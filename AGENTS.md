# Book Match — Agent guide

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

```
Book_Match/
├── backend/           # Flask API (Python)
│   ├── __init__.py        # create_app(), security headers, routes
│   ├── config.py          # Config class, env vars, _require(), _resolve_database_uri()
│   ├── extensions.py      # db, jwt, limiter singletons
│   ├── models.py          # 9 models: User, UserProfile, UserStats, Mission,
│   │                      #   Challenge, Badge, UserMissionProgress,
│   │                      #   UserChallengeProgress, UserBadge, ReadingDay
│   ├── auth_routes.py     # POST /api/auth/{register,login,logout,refresh}
│   ├── auth_service.py    # bcrypt hash/verify (cost 12), register, authenticate
│   ├── validators.py      # email, password (≥8, 1 hoa, 1 thường, 1 số), full_name
│   ├── user_routes.py     # Profile, missions, timer, streak, books
│   ├── ai_routes.py       # GET/POST /api/ai/recommendations (rate limited)
│   ├── ai_service.py      # Build system prompt (seasonal), parse Ollama JSON response
│   ├── ollama_service.py  # chat_completion() → /api/chat, extract_json() handles fences
│   ├── gamification_service.py  # Streak, XP, badge unlock, challenge sync
│   └── seed_data.py       # 10 missions, 3 challenges, 6 badges (idempotent)
├── template/           # 8 HTML pages (Tailwind CSS CDN, Material Symbols icons)
│   ├── welcome.html    # Landing page (hero, features, reviews, CTA auth popup)
│   ├── index.html      # AI survey (tuổi, sở thích, tâm trạng)
│   ├── login.html      # Login form + password toggle + OAuth placeholders
│   ├── signup.html     # Registration form
│   ├── home.html       # AI recommendations grid + refresh/delete + bottom CTA
│   ├── mission.html    # Daily missions, challenges, badges grid
│   ├── timer.html      # SVG circular Pomodoro timer + cancel popup
│   └── streak.html     # Monthly calendar, stats, milestone progress
├── static/js/
│   ├── api.js          # AppApi singleton: get/post/put, auto CSRF from cookie
│   ├── auth.js         # Login/signup form binding, password toggle, OAuth stubs
│   └── app.js          # 6 page controllers (data-page attr), header streak badge
├── tests/
│   ├── conftest.py     # In-memory SQLite fixture, env vars for test
│   └── test_auth_security.py  # 11 tests: password, SQLi, duplicate, cookies, headers
├── docs/               # 5 markdown files: auth, backend, gamification, ollama, security
└── data/app.db         # SQLite auto-created on startup
```

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
- Each HTML has inline `tailwind.config` (Material Design 3 color scheme, Montserrat font, custom spacing)
- Page controller selected via `<body data-page="...">` in `app.js`

### app.js controllers

| `data-page` | Function | API calls |
|-------------|----------|-----------|
| `home` | `initHome()` | GET `/api/ai/recommendations`, POST `/api/ai/recommendations/refresh` |
| `survey` | `initSurvey()` | PUT `/api/user/profile` |
| `mission` | `initMissions()` | GET `/api/user/missions` |
| `timer` | `initTimer()` | GET `/api/user/timer/active`, POST `/api/user/timer/complete` |
| `streak` | `initStreak()` | GET `/api/user/streak?year=&month=` |

### AI cache mechanism

- Recommendations cached in `localStorage` key `ai_recommendations_cache`
- Survey submission sets `ai_needs_refresh=1` flag to trigger fresh AI call on home
- Survey profile also cached in `localStorage` key `survey_profile` for pre-fill

## Gamification

- Timer completion requires activating a mission first: `POST /api/user/missions/<id>/activate`
- Streaks calculated from `ReadingDay` records in `gamification_service.py:_update_streak()`
- Badges, challenges, missions seeded idempotently in `seed_data.py`
- Badge unlock rules in `gamification_service.py:_try_unlock_badges()` — 6 conditions checked
- Challenge sync in `_sync_challenges()` — 3 challenges: streak-7, hours-10, books-2-month

## AI / Ollama

- Calls `{OLLAMA_BASE_URL}/api/chat` with system + user messages
- System prompt includes current date (seasonal recommendations)
- Response parsed by `extract_json()` — handles markdown code fences and bare JSON
- Default model: `llama3.2` (override via `OLLAMA_MODEL`)
- Prerequisite: `ollama serve` running locally
- Rate limited: GET 30/h, POST 20/h

## Security

- **bcrypt** cost 12, no plaintext in logs/responses
- **JWT**: HttpOnly cookie, SameSite=Lax, CSRF in cookie, access 15 min, refresh 7 days
- **Rate limit**: 10/min auth, 30/h AI GET, 20/h AI POST
- **Headers**: X-Frame-Options: DENY, X-Content-Type-Options: nosniff, HSTS (conditional on HTTPS), Permissions-Policy
- **Generic login errors**: same message for wrong password and non-existent email

## Testing

- `pytest tests/ -v` — 11 tests in `test_auth_security.py`
- Contains tests for:
  - Weak password rejection
  - SQL injection resistance
  - Duplicate email (409)
  - Generic login error (wrong password AND non-existent email)
  - Password hash not leaked
  - Unauthenticated access blocked (401)
  - HttpOnly cookie set on login
  - Security headers present
  - Password mismatch rejected
  - Authenticated /api/auth/me after register
- Missing test coverage: gamification service, AI service, user routes (profile CRUD, missions, timer, streak)

## Know issues / notes

- Tailwind config duplicated inline in all 8 HTML files (~60 lines each)
- `scripts/` directory is empty
- Timer uses `setInterval(..., 200)` — minor drift but acceptable for MVP
- `app.js` ~540 lines — candidate for modularization
- No dark mode toggle despite `darkMode: "class"` in config
- OAuth buttons show "Tính năng đang phát triển" alert
- Forgot password shows "Vui lòng liên hệ với Quản trị viên" alert
- Footer links (Điều khoản, Chính sách bảo mật, Liên hệ) all show "Đang cập nhật" popup

## Production checklist

- PostgreSQL instead of SQLite, Redis for rate limit storage
- `JWT_COOKIE_SECURE=true` for HTTPS
- Generate secrets via `secrets.token_hex(32)`
