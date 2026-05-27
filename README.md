# DigiPros — Backend

FastAPI + SQLAlchemy + SQLite. Email/password, Google, and Apple Sign In —
all issue the same first-party JWT used by the frontend.

## Structure

```
Backend/
├── requirements.txt
├── .env.example
└── app/
    ├── main.py              # FastAPI app, CORS, session, router mounts
    ├── config.py            # env settings (pydantic-settings)
    ├── database.py          # engine, SessionLocal, get_db()
    ├── models.py            # User (company account), QuoteRequest
    ├── schemas.py           # request/response models
    ├── security.py          # bcrypt hashing + JWT (HS256)
    ├── deps.py              # get_current_user dependency
    ├── services_catalog.py  # static list of marketing services
    └── routers/
        ├── auth.py          # POST /auth/signup · /auth/login · GET /auth/me
        ├── oauth.py         # /auth/google · /auth/apple · /auth/providers
        ├── users.py         # GET/PUT /users/me (company + contact)
        ├── services.py      # GET /services · GET /services/{slug}
        ├── quotes.py        # POST/GET /quotes
        └── analytics.py     # GET /analytics/me (placeholder metrics)
```

Accounts are **company-based** — one company == one account. The
`User` table stores both the login identity (email/password or OAuth)
and the company it represents (company_name, industry, revenue, etc).
There is no separate Business table.

## Run locally

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env            # on Windows use: copy .env.example .env
uvicorn app.main:app --reload   # http://localhost:8000  (docs: /docs)
```

The first run creates `digipros.db` (SQLite). To switch to Postgres later,
just change `DATABASE_URL` — no code changes.

## Endpoints

| Method | Path                       | Description                                                                |
| ------ | -------------------------- | -------------------------------------------------------------------------- |
| POST   | `/auth/signup`             | Create company account: `{email, password, contact_name?, company_name, …}` |
| POST   | `/auth/login`              | `{email, password}` → `{access_token}`                                     |
| GET    | `/auth/me`                 | Bearer token → current user                                                |
| GET    | `/auth/providers`          | Which OAuth providers are configured                                       |
| GET    | `/auth/google/login`       | Redirect to Google                                                         |
| GET    | `/auth/google/callback`    | Google → `FRONTEND_URL/auth/callback?token=…`                              |
| GET    | `/auth/apple/login`        | Redirect to Apple                                                          |
| POST   | `/auth/apple/callback`     | Apple → `FRONTEND_URL/auth/callback?token=…`                               |
| GET    | `/users/me`                | Current company account (login + company fields)                           |
| PUT    | `/users/me`                | Update company info and contact details                                     |
| GET    | `/services`                | List all DigiPros services                                                 |
| GET    | `/services/{slug}`         | Detail for a single service                                                |
| POST   | `/quotes`                  | Submit a quote request                                                     |
| GET    | `/quotes`                  | List the caller's quote requests                                           |
| GET    | `/analytics/me`            | Placeholder analytics snapshot for the client portal                       |

## OAuth setup (only when you're ready to enable each)

**Google** — [Cloud Console](https://console.cloud.google.com) → APIs & Services
→ Credentials → OAuth client (Web). Authorized redirect URI:
`http://localhost:8000/auth/google/callback` (and your production URL).
Drop the client ID/secret into `.env`.

**Apple** — [developer.apple.com](https://developer.apple.com) → Identifiers
→ create a Services ID (this is `APPLE_CLIENT_ID`) → enable Sign In with
Apple → return URL `http://localhost:8000/auth/apple/callback`. Create a
Sign-In key (`.p8`), note `APPLE_KEY_ID` and your `APPLE_TEAM_ID`, paste
the full `.p8` body into `APPLE_PRIVATE_KEY`.

If a provider isn't configured, its endpoints return `503` and the
frontend simply hides that button.
