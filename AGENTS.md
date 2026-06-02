# Open WebUI — Agent Instructions

## Repo structure

- **`backend/`** — FastAPI Python backend (`backend/open_webui/main.py` is the app entrypoint, `open_webui:app` via typer)
- **`src/`** — SvelteKit 2 + Vite 5 frontend (Svelte 5 runestore)
- **`docker-compose.yaml`** — default dev deployment orchestration
- Version is synced between `package.json` and `pyproject.toml` via hatch metadata

## Prerequisites

- Node 18–22 (`engine-strict=true` enforced via `.npmrc`)
- Python 3.11 or 3.12 (`< 3.13`)
- npm uses `npm ci --force` in CI to bypass engine-strict
- For production builds: `npm run build` always runs `npm run pyodide:fetch` first (see package.json scripts)

## Commands

### Frontend

| Task | Command |
|------|---------|
| Install deps | `npm ci` |
| Dev server | `npm run dev` (also runs `pyodide:fetch` automatically) |
| Build | `npm run build` |
| Typecheck | `npm run check` (runs `svelte-kit sync` + `svelte-check`) |
| Lint + format | `npm run format` (Prettier — single quotes, trailing commas) |
| Unit tests | `npm run test:frontend` (vitest) |
| i18n extraction | `npm run i18n:parse` |

### Backend

| Task | Command |
|------|---------|
| Lint | `npm run lint:backend` (pylint) or `ruff check backend/` |
| Format | `npm run format:backend` (ruff format, excludes .venv/venv) |
| Pre-commit | `npm run format:backend` + `ruff check --fix backend/` (via `.pre-commit-config.yaml`) |

### Full verification

```bash
npm run lint       # frontend + typecheck + backend pylint (OR)
make startAndBuild # docker-compose up --build -d
```

### Docker / Compose

```bash
make install      # docker-compose up -d
make startAndBuild  # docker-compose up -d --build
make remove       # docker-compose down (runs confirm_remove.sh)
```

Dev Docker run: `docker run -d -p 3000:8080 -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-westui/open-webui:main`

> **Arvoo system (different machine)**: prod uses `docker compose -f docker-compose.arvoo.yaml up -d`, dev uses `docker compose -f docker-compose.arvoo-dev.yaml up -d`. Don't run these during local development — they target a separate system.

## Testing quirks

- **Frontend tests**: vitest (`npm run test:frontend`). No separate `vitest.config.ts` — vitest uses vite.config.ts. No `.test.*` files found yet; vitest config is implicit from vite.
- **Backend tests**: pytest lives under `backend/open_webui/test/`. Integration tests (`AbstractPostgresTest`) require Docker for Postgres/Redis. The `all` optional deps include `pytest`, `pytest-docker`, `playwright`, `moto`, etc. Run selectively:
  ```bash
  pytest backend/open_webui/test/apps/webui/routers/test_users.py -v
  ```
- **E2E tests**: Cypress (`npm run cy:open`), targets `http://localhost:8080`

## Backend architecture notes

- **Routers**: `backend/open_webui/routers/` — 30+ route modules (chats, users, models, retrieval, audio, images, SCIM, etc.)
- **Models**: `backend/open_webui/models/` — SQLAlchemy/peewee hybrid ORM
- **Migrations**: alembic under `backend/open_webui/migrations/`
- **Storage providers**: S3/GCS/Azure/Local — configured via env vars, provider pattern in `storage/provider.py`
- **Env loading**: `backend/open_webui/env.py` loads `.env` from `BASE_DIR`. Key paths: `BACKEND_DIR = backend/`, `OPEN_WEBUI_DIR = backend/open_webui/`, `BASE_DIR = open-webui/`
- **DB**: SQLite default (`DATA_DIR/webui.db`), PostgreSQL optional via `DATABASE_URL` env var. DB migrations run on startup via alembic.
- **WebSocket support**: Redis-backed session management with optional Redis Sentinel/cluster
- **Secret key**: auto-generated on first run in `.webui_secret_key` within CWD, overridable via `WEBUI_SECRET_KEY` env var

## Frontend notes

- Uses **Svelte 5 runes**; imports follow `import { ... } from './components/...'` pattern
- **API layer**: `src/lib/apis/` mirrors backend router structure
- **Stores**: `src/lib/stores/` for Svelte writable stores
- **i18n**: `src/lib/i18n/`, translations extracted via `i18next-parser` + Prettier
- **Tailwind CSS v4** with `@tailwindcss/postcss` and `svelte` plugin
- **TipTap** for rich text editor, **CodeMirror** for Python code editor (pyodide runtime)
- **Vite build**: runs `adapter-static` with `build/index.html` fallback

## Environment variables (commonly modified)

| Variable | Purpose |
|----------|---------|
| `OLLAMA_BASE_URL` | Ollama endpoints |
| `OPENAI_API_BASE_URL` / `OPENAI_API_KEY` | OpenAI-compatible API |
| `CORS_ALLOW_ORIGIN` | CORS policy (defaults to `*`) |
| `DATABASE_URL` | External DB |
| `REDIS_URL` | Redis for sessions/websockets |
| `WEBUI_SECRET_KEY` | JWT secret (auto-generated if unset) |
| `WEBUI_AUTH` | Enable/disable auth (`true` default) |
| `ENABLE_SCIM` / `SCIM_TOKEN` | SCIM provisioning |

## Gotchas

- `pip install pyodide` requires fetching assets (`npm run pyodide:fetch`) — dev server does this automatically
- `aiohttp==3.13.3` is pinned **below** 3.13.3 in `pyproject.toml` (broken version)
- `pyarrow==20.0.0` is pinned for RPi compatibility
- Python formatting uses **single quotes** (ruff config)
- Backend lint uses **line-length 120** (black + ruff)
- `npm run lint` runs **frontend + typecheck + backend** sequentially (runs both `;` separated commands)
- Docker compose has many variants: GPU, AMDGPU, API-only, Arvoo, OTEL — see `docker-compose.*.yaml`
- Version bump: change `package.json` version; hatch reads it automatically via `tool.hatch.version`

## Existing instruction sources

No `CLAUDE.md`, `.cursorrules`, or existing `AGENTS.md` found. No `opencode.json` config.
