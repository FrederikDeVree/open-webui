# PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-02

## OVERVIEW
Project: **Open WebUI** — A feature-rich, self-hosted AI web interface with built-in RAG, offline capabilities, and extensibility via plugins. Designed to operate entirely offline with support for Ollama, OpenAI-compatible APIs, and 9 vector databases.

Stack: **SvelteKit 2 + Svelte 5** (frontend), **FastAPI + Python 3.11/3.12** (backend), **SQLite/PostgreSQL** (database), **TailwindCSS 4** (styling), **Docker** (deployment), **Vite 5** (build), **TypeScript** (types), **Cypress** (E2E tests)

## STRUCTURE
```
open-webui/
├── src/                    # SvelteKit frontend source
│   ├── lib/                # Shared libraries: stores, components, types, utils, APIs
│   ├── routes/             # SvelteKit page routes (+page.svelte, +layout.svelte)
│   ├── app.css             # Global styles
│   ├── app.html            # HTML entry point
│   └── app.d.ts            # TypeScript declarations
├── backend/                # Python backend source
│   ├── open_webui/         # Main package: routers, models, utils, storage
│   │   ├── routers/        # FastAPI route handlers (one per domain)
│   │   ├── models/         # SQLAlchemy ORM models (access_grants, chats, users, etc.)
│   │   ├── utils/          # Backend utilities (auth, embeddings, middleware, etc.)
│   │   ├── socket/         # WebSocket handlers
│   │   ├── main.py         # FastAPI app entry point (uses context manager lifecycle)
│   │   └── env.py          # Environment variable loading and configuration
│   ├── data/               # Runtime data (databases, storage)
│   └── requirements.txt    # Python dependencies
├── docs/                   # Documentation
├── scripts/                # Build/utility scripts (pyodide fetch, etc.)
├── cypress/                # Cypress E2E test fixtures
├── static/                 # Static assets
├── test/                   # Test files
├── docker-compose*.yaml    # Docker Compose configurations (dev, GPU, Playwright, etc.)
├── Dockerfile              # Multi-stage Docker build (Node frontend + Python backend)
├── pyproject.toml          # Python project config (hatch, ruff, black, codespell)
├── svelte.config.js        # SvelteKit config (adapter-static)
├── vite.config.ts          # Vite build config
├── tailwind.config.js      # TailwindCSS config (typography + container queries plugins)
├── postcss.config.js       # PostCSS with Tailwind
├── tsconfig.json           # TypeScript config (extends .svelte-kit/tsconfig.json)
├── .eslintrc.cjs           # ESLint: typescript-eslint + svelte + cypress + prettier
└── i18next-parser.config.ts # Internationalization config
```

**Key directories:**
*   `src/lib/stores/` — Svelte writable stores (config, user, socket, theme, models, tools, etc.). Central state management.
*   `src/lib/components/` — Reusable Svelte components (chat, admin, layout, modals, icons).
*   `src/lib/apis/` — API client modules for frontend→backend communication.
*   `backend/open_webui/routers/` — FastAPI API routers (chats, users, tools, models, prompts, knowledge, files, etc.).
*   `backend/open_webui/models/` — SQLAlchemy ORM models.
*   `backend/open_webui/utils/` — Backend utilities (auth, middleware, embeddings, logger, access_control, etc.).

## COMMANDS
| Action | Command |
|--------|---------|
| Install (frontend) | `npm ci` |
| Install (backend) | `pip install -r backend/requirements.txt` |
| Build | `npm run build` (Vite+SvelteKit, also fetches Pyodide) |
| Run (dev frontend) | `npm run dev` (or `npm run dev:5050` on port 5050) |
| Run (Docker) | `docker compose up` or `./run.sh` |
| Lint | `npm run lint` (frontend + types + backend) |
| Format (JS/TS/Svelte) | `npm run format` |
| Format (Python) | `npm run format:backend` |
| Test (frontend) | `npm run test:frontend` (Vitest) |
| E2E tests | `npm run cy:open` (Cypress) |
| Type check | `npm run check` (svelte-check) |
| i18n parse | `npm run i18n:parse` |

## CODING STANDARDS

### Frontend (TypeScript / Svelte 5)
*   **Framework**: SvelteKit with Svelte 5 runes. Components use `.svelte` files with `<script lang="ts">` and `<style>` blocks.
*   **State**: Svelte writable stores in `src/lib/stores/`. Stores are exported from `$lib/stores/index.ts`.
*   **Styling**: TailwindCSS 4 with `@tailwindcss/typography` and `@tailwindcss/container-queries` plugins. Dark mode via class strategy.
*   **Build**: Vite 5 with `@sveltejs/kit`. Adapter-static for static output.
*   **Linting**: ESLint with `@typescript-eslint`, `eslint-plugin-svelte`, `eslint-plugin-cypress`, and `prettier`. Prettier also handles formatting.
*   **TypeScript**: Strict mode enabled, extends `.svelte-kit/tsconfig.json`.
*   **i18n**: `i18next-parser` config for translations. Translations in `src/lib/i18n/`.

### Backend (Python 3.11/3.12)
*   **Framework**: FastAPI with Uvicorn ASGI server.
*   **ORM**: SQLAlchemy 2.0+ with async support. Alembic for migrations. Also supports Peewee.
*   **Database**: SQLite (default, async via aiosqlite) or PostgreSQL (via psycopg). Also supports PyMySQL (MariaDB), MongoDB.
*   **Styling**: Black (line-length 120, double quotes) + Ruff (line-length 120, single quotes for code). Google-style docstrings (pydocstyle convention).
*   **Linting**: Ruff (selects E/W/I/UP/C90/Q/ICN), pylint via npm script. Codespell for typos.
*   **Logging**: Loguru with custom structured logging.
*   **Dependencies**: Managed via `pyproject.toml` (hatchling build). Version pinned in `requirements.txt` too.
*   **Environment**: `.env` file via python-dotenv. Heavy use of `os.environ` in `backend/open_webui/env.py`.

### Architecture Patterns
*   **Frontend-backend split**: SvelteKit frontend serves static files; Python FastAPI backend at `/api`. CORS configured in `main.py`.
*   **API routes**: One FastAPI router file per domain (e.g., `chats.py`, `users.py`, `tools.py`). Mounted in `main.py`.
*   **WebSocket**: Socket.io-based real-time communication in `backend/open_webui/socket/`.
*   **Session management**: Redis-backed (with starlette/sessions fallback). Session pooling via `session_pool.py`.
*   **Middleware chain**: AuthTokenMiddleware, CommitSessionMiddleware, RedirectMiddleware, WebsocketUpgradeGuardMiddleware, AuditLoggingMiddleware, CORSMiddleware, CompressMiddleware, SessionMiddleware.
*   **Database migrations**: Alembic + Peewee-migrate. Config in `alembic.ini` and `migrations/`.

## WHERE TO LOOK
*   **Frontend source**: `src/`
*   **Backend source**: `backend/open_webui/`
*   **Tests**: `cypress/` (E2E), `test/` (backend test files), `vitest` config via `npm run test:frontend`
*   **Docs**: `docs/` — also external docs at https://docs.openwebui.com/
*   **Docker configs**: `docker-compose.yaml` (default), `Dockerfile` (multi-stage build), plus variant compose files
*   **Environment config**: `backend/open_webui/env.py` (all backend env vars defined here)
*   **Frontend stores (state)**: `src/lib/stores/index.ts` — the "single source of truth" for frontend state
*   **Python deps**: `pyproject.toml` (canonical) + `backend/requirements.txt`

## NOTES
*   **⚠️ No Docker Compose on this machine**: Docker Compose is not available in this dev environment. The test environment runs on a separate remote machine. Do not attempt to run `docker compose` commands here — only use them on the designated test machine.
*   **Multi-stage Docker build**: Frontend builds first (node:22-alpine3.20), then backend bundles with frontend assets into Python wheel via hatch.
*   **Version source**: Python version is read from `package.json` via hatch's dynamic version.
*   **Pyodide**: Frontend fetches Pyodide assets during build (`npm run pyodide:fetch` / `scripts/prepare-pyodide.js`).
*   **HMR/Dev**: `vite.config.ts` strips `console.log/debug/error` in production but not in dev (`ENV=dev`).
*   **Tailwind 4**: Uses PostCSS plugin (`@tailwindcss/postcss`) — not the native CSS-first approach despite Tailwind 4.
*   **Key dependencies**: Ollama (default LLM runner), OpenAI/Anthropic/Google GenAI (API providers), LangChain (tool integrations), ChromaDB/Qdrant/etc. (vector DBs), Redis (sessions), SQLite (default DB).
*   **Svelte 5**: Uses `<script lang="ts">` syntax. Reactive statements via `:bind:`, `onMount`, `tick`, etc. Context API via `getContext('i18n')`.
*   **Enterprise features**: LDAP/AD, SCIM 2.0, RBAC with granular permissions, audit logging, OpenTelemetry support.
