# Frndly — Backend API

FastAPI backend for Frndly. Handles auth, clipboard sync, and encrypted secret vault.

## Stack

- **Python 3.12** + **uv** (package manager)
- **FastAPI** + **Uvicorn** (port `8004`)
- **SQLAlchemy 2.0** async + **asyncpg**
- **Alembic** migrations
- **Pydantic v2** schemas
- **bcrypt** password hashing
- **python-jose** JWT auth
- **Fernet** encryption for vault values at rest
- **PostgreSQL 15** via Docker (port `5439`)

## Ports

| Service  | Port |
|----------|------|
| API      | 8004 |
| Postgres | 5439 |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Setup

### 1. Clone / enter the repo

```bash
cd /path/to/frndly-be
```

### 2. Create Python virtual environment

```bash
uv venv --python 3.12
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv sync
```

Or using pip-compatible requirements:

```bash
uv pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` — minimum required:

```env
DATABASE_URL=postgresql+asyncpg://frndly:frndly@localhost:5439/frndly
JWT_SECRET_KEY=replace_me_with_a_strong_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=http://localhost:8081,http://localhost:19006
```

### 5. Start PostgreSQL

```bash
docker compose up -d
```

Verify it's healthy:

```bash
docker compose ps
```

### 6. Run database migrations

```bash
uv run alembic upgrade head
```

### 7. Start the API server

```bash
uv run uvicorn app.main:app --reload --port 8004
```

API is now live at `http://localhost:8004`

Interactive docs: `http://localhost:8004/docs`

---

## Development Shortcuts (Makefile)

```bash
make up       # start Docker postgres
make down     # stop Docker postgres
make dev      # start postgres + API server (port 8004)
make migrate  # run alembic upgrade head
make reset    # destroy DB volume, restart fresh, re-migrate
```

---

## API Endpoints

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/signup` | — | Register new user |
| POST | `/api/v1/auth/login` | — | Login, returns JWT |
| GET | `/api/v1/auth/me` | Bearer | Get current user |

### Clipboard
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/clipboard` | Bearer | List clipboard items (paginated, searchable) |
| POST | `/api/v1/clipboard` | Bearer | Push new clipboard item |
| DELETE | `/api/v1/clipboard/{id}` | Bearer | Delete item |

### Vault
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/secrets` | Bearer | List secrets (filter by search/category) |
| POST | `/api/v1/secrets` | Bearer | Create secret (value encrypted at rest) |
| PUT | `/api/v1/secrets/{id}` | Bearer | Update secret metadata |
| DELETE | `/api/v1/secrets/{id}` | Bearer | Delete secret |

### Users
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| PUT | `/api/v1/users/profile` | Bearer | Update name / email |

---

## Project Structure

```
frndly-be/
├── app/
│   ├── api/v1/         # Route handlers (auth, clipboard, vault, users)
│   ├── core/           # config, JWT security, request dependencies
│   ├── db/             # SQLAlchemy base + async session
│   ├── models/         # ORM models (User, ClipboardItem, Secret)
│   ├── repositories/   # DB query layer
│   ├── schemas/        # Pydantic request/response schemas
│   ├── services/       # Business logic (auth, clipboard, vault)
│   └── main.py         # FastAPI app + CORS
├── alembic/            # Migrations
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── Makefile
```

## Security Notes

- Passwords: `bcrypt` (never stored in plaintext)
- Secret values: encrypted with `Fernet` before DB insert, decrypted on read
- All protected endpoints require `Authorization: Bearer <token>` header
- JWT tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 24h)

## Connecting to Supabase (Production)

Replace `DATABASE_URL` in `.env` with your Supabase connection string:

```env
DATABASE_URL=postgresql+asyncpg://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

No code changes required.
