# Open WebUI — Agent Guide

## Stack

SvelteKit 2 + Svelte 5 + Vite (frontend) + FastAPI + SQLAlchemy (backend).
Single monorepo. Frontend lives in `src/`. Backend in `backend/open_webui/`.

## Setup

```
npm install --force    # --force is required
npm run dev            # frontend dev server (auto-fetches pyodide)
```

Python env: ≥3.11, <3.13. Use `uv` or `pip`. Install with `pip install -e ".[all]"` for dev extras.
Backend runs as a FastAPI app mounted by the same uvicorn server. For standalone backend: `cd backend && python -m open_webui dev`.

## Commands

| Command | What |
|---|---|
| `npm run dev` | Frontend dev server (port 5173) |
| `npm run build` | Production frontend build |
| `npm run lint` | Full lint suite: eslint → svelte-check → pylint |
| `npm run check` | `svelte-kit sync && svelte-check` (type check) |
| `npm run test:frontend` | Vitest unit tests |
| `npm run i18n:parse` | Extract and format translations |
| `npm run format` | Prettier frontend |
| `npm run format:backend` | Ruff format backend |

CI runs frontend and backend formatting checks separately.

## Architecture

- **Entry**: `backend/open_webui/__init__.py` exposes `serve`/`dev` CLI via typer. `backend/open_webui/main.py` creates the FastAPI app.
- **Frontend**: SvelteKit routes in `src/routes/(app)/`. Layout group `(app)` wraps authed pages.
- **Backend modules**: `routers/` (API endpoints), `models/` (DB models), `storage/`, `retrieval/` (RAG), `tools/`, `socket/` (websockets), `internal/`, `utils/`.
- **Database**: Default SQLite. Configurable to PostgreSQL (via `psycopg`), MariaDB. Migrations via Alembic in `backend/open_webui/migrations/`.
- **PWA**: `src/app.html` contains the splash screen and theme bootstrap logic (do not move out of that file).

## Dev Gotchas

- **Docker is prohibited on this machine**: This is a development workstation, not a test environment. Do not run `docker` or `docker compose` here — ever.
- **Python lock**: `aiohttp==3.13.3` is pinned bad in `pyproject.toml`. Do not update it.
- **Python versions**: Only 3.11 and 3.12 are supported; 3.13 is excluded.
- **i18n**: Extract with `npm run i18n:parse`. Translation keys live in `src/lib/i18n/`.
- **Tailwind 4**: Uses `@tailwindcss/postcss`, not `postcss.config.js` directives. Config in `tailwind.config.js`.
- **Docker compose**: Prefer `docker compose` over `docker-compose` (v2). Use `make install`/`make start`.
- **Pyodide**: Frontend dev/build scripts auto-fetch Pyodide via `npm run pyodide:fetch`. Do not skip this for Python-in-browser features.
- **Secret key**: Auto-generated at `backend/.webui_secret_key` on first `serve` if `WEBUI_SECRET_KEY` is unset.
- **CORS**: Set `CORS_ALLOW_ORIGIN` in `.env` for multi-origin local dev (`localhost:5173` + `localhost:8080`).

## File Conventions

- **Frontend**: Prettier (tabs, single quote, no trailing comma, 100 col). ESLint extends Prettier.
- **Backend**: Ruff (single quotes, line len 120). Black is configured but ruff-format is the active formatter.
- **Pre-commit**: Runs `ruff --fix` and `ruff format` on `backend/` only.
- **Svelte 5**: Uses runes (`$state`, `$derived`, `$effect`). Do not use Svelte 4 syntax in `.svelte` files.

## Testing

- Frontend: `npm run test:frontend` (vitest in `src/`).
- Backend: `pytest` under `backend/open_webui/test/`. Requires `[all]` extras (`playwright`, `docker`, etc.).
- E2E: Cypress tests in `cypress/` target `http://localhost:8080`.
- No frontend unit tests currently exist in a dedicated `__tests__/` directory — vitest runs alongside `src/` code.

## Env

Copy `.env.example` → `.env`. Key vars: `OLLAMA_BASE_URL`, `OPENAI_API_KEY`, `WEBUI_SECRET_KEY`, `CORS_ALLOW_ORIGIN`, `FORWARDED_ALLOW_IPS`.

## Branches

CI triggers on `main` and `dev` branches. See `.github/workflows/` for full pipeline definitions.
