# GitHub Searcher 🔍

A full-stack single-page application to search GitHub users and repositories in real-time, with Redis-backed server-side caching and Redux client-side caching.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + TypeScript, Vite, Vanilla CSS, Redux Toolkit, redux-persist, React Router, lodash |
| **Backend** | Django 5 + Django REST Framework |
| **Cache** | Redis (via django-redis), 2-hour TTL |
| **Docs** | drf-spectacular (OpenAPI / Swagger UI) |
| **Tests** | pytest-django + unittest.mock |
| **Infra** | Docker Compose |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Browser                                                │
│  React SPA ─── Redux Store ─── localStorage (persist)  │
│       │                                                  │
│       │  POST /api/search/                               │
│       ▼                                                  │
│  Django DRF ──► Redis Cache ──► GitHub REST API         │
└─────────────────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Two-layer caching**: The Redux store holds an in-memory cache keyed by `"query:entityType"`. Cache entries are persisted to `localStorage` via `redux-persist` so repeat searches survive page refreshes. The backend holds a Redis cache (2-hour TTL) so different browser sessions share results.

2. **Cache key design**: Both layers use `query.toLowerCase().trim() + ":" + entityType` — this makes `"Django"` and `"django"` share the same entry, and changing entity type with the same query correctly produces separate results.

3. **Debounce + min-chars**: The search fires after 400 ms of inactivity and only when ≥ 3 characters are typed. Switching entity type with an existing valid query fires immediately (debounce is cancelled).

4. **Graceful Redis degradation**: `IGNORE_EXCEPTIONS: True` in the cache config means the app continues to work if Redis is unavailable — it just won't cache.

5. **Vanilla CSS design system**: A single `index.css` defines all design tokens as CSS custom properties. Components consume them via `className`, keeping styles co-located but framework-free. Dark mode, glassmorphism cards, shimmer skeleton loaders, and floating hero animations are all pure CSS.

6. **No Django models required**: The app is stateless — all data comes from GitHub and lives in Redis. Only SQLite is configured to satisfy Django's requirement for a database, and no migrations are needed.

---

## Getting Started

### Prerequisites

- Docker & Docker Compose  
- **OR** Python 3.12+, Node.js 22+, and a running Redis instance

---

### Option A — Docker Compose (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/your-username/github-repo-search.git
cd github-repo-search

# 2. Create the backend .env file
cp backend/.env.example backend/.env
# Edit backend/.env and add your GITHUB_TOKEN

# 3. Start everything
docker-compose up
```

Open [http://localhost:5173](http://localhost:5173) for the frontend  
Open [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) for the Swagger UI

---

### Option B — Manual Setup

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set your GITHUB_TOKEN and REDIS_URL

# Run development server
python manage.py runserver
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

### `backend/.env`

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | (insecure default) | Django secret key — **change in production** |
| `GITHUB_TOKEN` | _(empty)_ | GitHub Personal Access Token — increases rate limit from 10 to 30 req/min |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Django allowed hosts |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |

---

## API Reference

### `POST /api/search/`

Search GitHub users or repositories.

**Request body:**
```json
{
  "query": "django",
  "entity_type": "repositories"
}
```

| Field | Type | Constraints |
|---|---|---|
| `query` | string | min 3, max 256 characters |
| `entity_type` | string | `"users"` or `"repositories"` |

**Response 200:**
```json
{
  "total_count": 12345,
  "entity_type": "repositories",
  "items": [...],
  "cached": false
}
```

---

### `POST /api/clear-cache/`

Flush all Redis-cached search results.

**Response 200:**
```json
{ "message": "Cache cleared successfully." }
```

---

### Swagger UI

Visit [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) for full interactive API documentation.

---

## Running Tests

```bash
cd backend

# Activate your virtualenv first
pip install -r requirements.txt

# Run tests with coverage
pytest

# Coverage report
pytest --cov=search --cov-report=html
open htmlcov/index.html
```

Test coverage includes:

- ✅ Happy path — repository search
- ✅ Happy path — user search
- ✅ Cache hit (GitHub API not called twice)
- ✅ Case-insensitive cache keys
- ✅ Different entity types produce separate cache entries
- ✅ Missing / invalid payload → 400
- ✅ GitHub rate limit → 429
- ✅ GitHub 502 error propagation
- ✅ Cache clear endpoint + invalidation verification
- ✅ GitHub client unit tests (timeout, 403, invalid entity type)

---

## Project Structure

```
github-repo-search/
├── backend/
│   ├── config/
│   │   ├── settings.py       # Django settings, Redis, CORS, DRF
│   │   └── urls.py           # Root URL config
│   ├── search/
│   │   ├── github_client.py  # GitHub REST API wrapper
│   │   ├── serializers.py    # DRF serializers
│   │   ├── views.py          # SearchView + ClearCacheView
│   │   ├── urls.py           # /api/search/ + /api/clear-cache/
│   │   └── tests/
│   │       └── test_views.py # Full unit test suite
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── searchApi.ts       # Axios client
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── SearchBar.tsx      # Debounced, entity-aware input
│   │   │   ├── RepoCard.tsx       # Repository result card
│   │   │   ├── UserCard.tsx       # User result card
│   │   │   ├── ResultsGrid.tsx    # Grid + all states
│   │   │   └── SkeletonGrid.tsx   # Shimmer loader
│   │   ├── store/
│   │   │   ├── index.ts           # Redux store + redux-persist
│   │   │   ├── searchSlice.ts     # Async thunk + cache logic
│   │   │   └── hooks.ts           # Typed useAppDispatch/Selector
│   │   ├── types.ts               # Shared TypeScript interfaces
│   │   ├── App.tsx                # Root layout (hero ↔ compact)
│   │   ├── main.tsx               # React entry point
│   │   └── index.css              # Full design system (Vanilla CSS)
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

---

## Deployment

### Frontend → Vercel

```bash
cd frontend
npm run build
# Deploy dist/ to Vercel, set VITE_API_BASE_URL to your backend URL
```

### Backend → Railway / Render

Set environment variables (`GITHUB_TOKEN`, `REDIS_URL`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`) and deploy the `backend/` directory.

---

## License

MIT