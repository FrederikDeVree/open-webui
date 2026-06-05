# PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-03

## OVERVIEW
Project: **Open WebUI**
Stack: **Svelte 5** (frontend) + **FastAPI** (Python backend), **TypeScript**, **Tailwind CSS v4**, **Vite**, **Pyodide**, **i18next**
Node: `>=18.13.0 <=22.x.x` | Python: `3.11, 3.12` (no 3.13+)

Open WebUI is a self-hosted, offline-first AI web interface. The backend is a Python FastAPI app; the frontend is a SvelteKit PWA. They are served together in production.

## STRUCTURE

```
open-webui/
├── backend/                  # Python backend (FastAPI + uvicorn)
│   ├── open_webui/           # Main application package (~222 .py files)
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── __init__.py       # CLI entry (typer + uvicorn)
│   │   ├── config.py         # Configuration layer (AppConfig, ConfigTable)
│   │   ├── env.py            # Env loading, path resolution, feature flags
│   │   ├── models/           # SQLAlchemy/Peewee DB models (~25 files)
│   │   ├── routers/          # API route handlers (~33 files)
│   │   ├── socket/           # WebSocket handlers
│   │   ├── tools/            # Built-in Python tools (function calling)
│   │   ├── retrieval/        # RAG: vector DBs, embedding, search
│   │   ├── storage/          # S3/GCS/Azure blob storage backends
│   │   ├── migrations/       # Alembic migrations
│   │   └── internal/         # Internal helpers (config tables, SCIM)
│   ├── start.sh              # Production start script
│   └── dev.sh                # Dev server (uvicorn --reload)
├── src/                      # SvelteKit frontend (~584 .svelte, ~74 .ts)
│   ├── app.html              # HTML entry (splash screen, theme init)
│   ├── app.css               # Global CSS
│   ├── routes/               # SvelteKit file-based routing
│   │   ├── (app)/            # Authenticated app routes
│   │   ├── auth/             # Login, register, OAuth flows
│   │   └── watch/            # Embedded watch mode
│   └── lib/                  # Shared library
│       ├── components/       # UI components (admin, chat, workspace, common, icons)
│       ├── apis/             # API client modules
│       ├── stores/           # Svelte writable/readable stores
│       ├── types/            # TypeScript type definitions
│       ├── utils/            # Utility functions
│       ├── constants.ts      # App constants (base URLs, file types)
│       └── i18n/             # Internationalization (i18next)
├── static/                   # Static assets (favicons, splash images, loader)
├── docs/                     # OpenAPI / security docs
├── scripts/                  # Build/dev scripts (pyodide fetch, etc.)
├── test/                     # Test fixtures/files
└── tools/                    # Utility tools
```

## COMMANDS

*WARNING:* do not grep, tail or head directly on the output of a command but output the result to disk, and select the relevant portion of the output there. Most cmmands are *slow*!

### Install

| Action           | Command |
|------------------|---------|
| Install deps (FE) | `npm install` |
| Install deps (BE) | `pip install -e "backend[all]"` or `uv pip install -e ".[dev]"` |

### Development

| Action           | Command | Notes |
|------------------|---------|-------|
| Dev server (FE)  | `npm run dev` | Port 5173; auto-runs `pyodide:fetch` first |
| Dev server (FE, alt port) | `npm run dev:5050` | Port 5050 |
| Dev server (BE)  | `cd backend && ./dev.sh` | `uvicorn --reload` on port 8080 |
| Fetch Pyodide assets | `npm run pyodide:fetch` | Run by `dev`/`build` automatically via `scripts/prepare-pyodide.js` |

### Build & Preview

| Action           | Command | Notes |
|------------------|---------|-------|
| Build            | `npm run build` | Auto-runs `pyodide:fetch` first |
| Build (watch)    | `npm run build:watch` | Incremental rebuild on file change |
| Preview          | `npm run preview` | Serves the `build/` output locally |

### Quality

| Action           | Command | Notes |
|------------------|---------|-------|
| Type check       | `npm run check` | SvelteKit sync + svelte-check |
| Type check (watch) | `npm run check:watch` | Re-checks on every save |
| Lint (all)       | `npm run lint` | Runs `lint:frontend`, `lint:types`, `lint:backend` in sequence |
| Lint frontend    | `npm run lint:frontend` | ESLint with auto-fix |
| Lint types       | `npm run lint:types` | Alias for `check` |
| Lint backend     | `npm run lint:backend` | Pylint on `backend/` |
| Format (FE)      | `npm run format` | Prettier — JS/TS/Svelte/CSS/MD/HTML/JSON |
| Format (BE)      | `npm run format:backend` | Ruff format (excludes `.venv`) |

### Testing

| Action           | Command | Notes |
|------------------|---------|-------|
| Frontend tests   | `npm run test:frontend` | Vitest (`--passWithNoTests`) |
| E2E tests        | `npm run cy:open` | Cypress interactive runner |
| i18n extract     | `npm run i18n:parse` | Extracts strings + Prettier-formats output |

### Docker

| Action           | Command |
|------------------|---------|
| Docker install   | `make install` (docker compose up -d) |
| Docker run       | `make start` |
| Docker build+run | `make startAndBuild` |
| Docker update    | `make update` |

## CODING STANDARDS

### Frontend (TypeScript / Svelte)
- **Framework**: Svelte 5 with runes (`$state`, `$derived`, `$effect`). Uses `<script context="module">` for module-level code.
- **Language**: TypeScript (strict mode). Path aliases via `$lib/`, `$app/`, `$env/`.
- **Styling**: Tailwind CSS v4 + PostCSS. CSS variables for theming (light/dark/oled/her themes). Scoped via Svelte's built-in compilation.
- **Linting**: ESLint (`@typescript-eslint`, `plugin:svelte`, `prettier`).
- **Formatting**: Prettier — single quotes, tabs, max width 100, no trailing comma. Svelte files use `prettier-plugin-svelte`.
- **State**: Svelte stores in `src/lib/stores/` (writable/readable). Context API for cross-component injection (e.g., `getContext('i18n')`).
- **Components**: Located in `src/lib/components/`. Organized by feature area (chat, workspace, admin, common).
- **API clients**: `src/lib/apis/` — functions that call backend endpoints via `WEBUI_API_BASE_URL`.

### Backend (Python)
- **Framework**: FastAPI + Uvicorn. Typer for CLI.
- **Language**: Python 3.11/3.12. Type hints with `from __future__ import annotations`. Google-style docstrings.
- **ORM**: SQLAlchemy 2.x (async) with aiosqlite (default). PostgreSQL via psycopg3. Also Peewee for some legacy models.
- **Migrations**: Alembic (see `backend/open_webui/alembic.ini`).
- **Linting**: Ruff (pycodestyle E, pyflakes F, isort I, pyupgrade UP, McCabe <=10). Quote style: single.
- **Formatting**: Black (line-length 120, single quotes).
- **Architecture**: Routers in `routers/` (FastAPI APIRouter), models in `models/` (SQLAlchemy), utilities in `utils/`, tools in `tools/`.
- **Config**: Environment-driven via `env.py` (.env file + os.environ). App-level config in `config.py`.
- **Auth**: JWT via `python-jose`, OAuth2 via `authlib`, argon2 for password hashing.

## WHERE TO LOOK

| Area        | Path |
|-------------|------|
| **Frontend source** | `src/` |
| **Backend source** | `backend/open_webui/` |
| **Svelte components** | `src/lib/components/` |
| **Svelte routes** | `src/routes/` |
| **API routers** | `backend/open_webui/routers/` |
| **DB models** | `backend/open_webui/models/` |
| **Stores (frontend state)** | `src/lib/stores/` |
| **i18n** | `src/lib/i18n/` + `i18next-parser.config.ts` |
| **Static assets** | `static/` |
| **Docker / deploy** | `Dockerfile`, `docker-compose.yaml`, `.env.example` |
| **Build config** | `vite.config.ts`, `svelte.config.js`, `tailwind.config.js` |
| **Python deps** | `pyproject.toml` |
| **JS deps** | `package.json` |
| **Docs** | `docs/`, https://docs.openwebui.com |

## NOTES

- **Production mode**: The Python backend (FastAPI) serves the built SvelteKit frontend statically. Frontend and backend share the same host/port.
- **Dev mode**: Vite runs the frontend dev server (port 5173). Uvicorn runs the backend (port 8080). CORS is configured for `localhost:5173` + `localhost:8080`.
- **Database**: Defaults to SQLite (aiosqlite). PostgreSQL supported via `psycopg[binary]`. Data persists in `backend/open_webui/data/`.
- **Vector DBs**: Supports 9 backends (Chroma, Qdrant, PGVector, Milvus, Elasticsearch, OpenSearch, Pinecone, S3, Oracle 23ai). Configured via env vars.
- **RAG**: Document ingestion uses `tiktoken` for tokenization, sentence-transformers/ONNX for embeddings. Parsing supports PDF, DOCX, PPTX, HTML, Markdown, Excel, and more.
- **WebSocket**: Socket.io for real-time chat streaming and notifications.
- **Redis**: Optional for session management and horizontal scaling.
- **PWA**: Supports offline access on localhost. Built with SvelteKit adapter-static.
- **Python CLI**: `open-webui serve [host] [port]` starts the production server. `open-webui dev` starts the dev server. `open-webui` is also importable as a package.
- **No project-level frontend test files found** (only `vitest` config for `test:frontend`). Cypress is available for E2E (`cy:open`).
- **Svelte 5**: Uses runes syntax (`$state`, `$derived`, `$effect`, `$props`, `$bindable`). Avoid legacy Svelte 4 patterns.
- **Environment**: See `.env.example` for all configurable variables. The `hatch_build.py` hooks customize the wheel build.
