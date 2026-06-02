# Repository Guidelines

## Project Overview

**Open WebUI** is a self-hosted AI web application providing a user-friendly interface for interacting with LLMs (Ollama, OpenAI, Anthropic, Google, etc.). It features RAG pipelines, vector search, web search, image generation, tool calling, OAuth/SCIM authentication, and a plugin system. The project is at version **0.9.5**.

- **Backend**: Python 3.11–3.12, FastAPI, SQLAlchemy async, Socket.IO
- **Frontend**: TypeScript, Svelte 5, SvelteKit 2, Vite 5, Tailwind CSS 4

## Architecture & Data Flow

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Svelte Frontend   │────▶│   FastAPI Backend  │────▶│  External APIs   │
│  (src/, Vite build) │     │  (backend/         │     │  OpenAI, Ollama, │
│                     │◀────│   main.py)         │◀────│  Anthropic, etc. │
│ Socket.IO real-time │     │                  │     └──────────────────┘
└─────────────────────┘     │  ┌────────────┐  │
                            │  │  Routers   │  │     ┌──────────────┐
                            │  │  (auths,   │  │────▶│  SQLAlchemy  │
                            │  │   chats,   │  │     │  Models      │
                            │  │   models)  │  │     │  (users,     │
                            │  └────────────┘  │     │   chats, etc)│
                            │  ┌────────────┐  │     └──────────────┘
                            │  │  Utils     │  │
                            │  │  (chat,    │  │     ┌──────────────┐
                            │  │   auth,   │  │────▶│  Vector DBs  │
                            │  │   oauth,  │  │     │  (pgvector,  │
                            │  │   plugin) │  │     │   qdrant,    │
                            │  └────────────┘  │     │   chroma...) │
                            │  ┌────────────┐  │     └──────────────┘
                            │  │  Socket.IO │  │
                            │  │  (main.py) │  │
                            │  └────────────┘  │
                            └──────────────────┘
```

**Key modules:**

| Module | Purpose |
|---|---|
| `backend/open_webui/main.py` | FastAPI app factory, lifespan, middleware, router mounting (2948 lines) |
| `backend/open_webui/env.py` | Runtime env vars, device detection (CUDA/MPS), JSON logging, changelog |
| `backend/open_webui/config.py` | Persistent config layer: `AppConfig` singleton, DB-backed settings, Alembic migrations |
| `backend/open_webui/routers/` | API endpoints — `auths`, `chats`, `models`, `users`, `tools`, `knowledge`, `scim`, `pipelines`, `automations` |
| `backend/open_webui/models/` | SQLAlchemy async ORM models + Pydantic v2 response wrappers |
| `backend/open_webui/utils/` | Cross-cutting concerns: `auth.py` (JWT, password hashing, DI), `chat.py` (completion pipeline, 5514 lines), `oauth.py` (OpenID Connect), `plugin.py` (dynamic function/tool loading), `asgi_middleware.py` (pure-ASGI middleware) |
| `backend/open_webui/retrieval/` | RAG pipeline: `vector/` (vector store adapters), `web/` (search providers), `loaders/` (YouTube, Tika, Docling) |
| `backend/open_webui/socket/` | Socket.IO server with Redis pub/sub for horizontal scaling |

**Patterns:**
- **Async-first**: all DB operations use SQLAlchemy 2.0 async
- **Dependency injection**: FastAPI `Depends()` throughout routers
- **Streaming**: SSE chunks via Socket.IO for real-time responses
- **Plugin system**: dynamic function/tool loading from disk or GitHub Gist with `pip install`
- **Two-layer config**: env vars for runtime, DB-backed `AppConfig` for admin UI changes
- **Pure-ASGI middleware**: avoids `Starlette BaseHTTPMiddleware` `CancelledError` leakage
- **Group-based access control**: hierarchical permissions with dot-separated keys

## Key Directories

| Path | Purpose |
|---|---|
| `backend/open_webui/` | Python backend (FastAPI app) |
| `backend/open_webui/routers/` | FastAPI route handlers (~28 files) |
| `backend/open_webui/models/` | SQLAlchemy models + Pydantic schemas |
| `backend/open_webui/utils/` | Shared utilities (auth, chat pipeline, OAuth, plugins) |
| `backend/open_webui/retrieval/` | RAG: vector stores, web search, document loaders |
| `backend/open_webui/socket/` | Socket.IO real-time infrastructure |
| `backend/open_webui/internal/` | Internal infra (database engine setup) |
| `src/` | Svelte frontend (SvelteKit) |
| `docs/` | Documentation, security policy |
| `.github/workflows/` | CI/CD pipelines |

## Development Commands

### Frontend (root `package.json`)

```bash
npm run dev                 # Start Vite dev server (fetches pyodide first)
npm run build               # Build for production
npm run check               # Type-check (svelte-kit sync + svelte-check)
npm run lint                # Run all linters (frontend + types + backend)
npm run format              # Format frontend files (Prettier)
npm run format:backend      # Format Python files (ruff format)
npm run i18n:parse          # Parse i18n translations
npm run cy:open             # Open Cypress UI
npm run test:frontend       # Run vitest (no-op if no tests)
```

### Backend (Python)

```bash
python -m open_webui serve              # Production server (Typer CLI)
bash backend/dev.sh                     # Dev server with --reload
python -m ruff check backend/           # Lint Python (ruff)
python -m ruff format backend/          # Format Python (ruff)
python -m black backend/                # Alternative formatter
pylint backend/                         # Backend lint (also run via npm run lint)
```

### Docker / Compose

```bash
make install            # docker compose up -d
make startAndBuild      # docker compose up -d --build
make stop               # docker compose stop
make remove             # docker compose down -v (with safety prompt)

# Full-featured orchestrator with GPU auto-detection:
./run-compose.sh --enable-gpu --enable-api --webui 3000 --build

# Alternative compose overlays:
# docker-compose.gpu.yaml          - NVIDIA GPU passthrough
# docker-compose.amdgpu.yaml       - AMD ROCm support
# docker-compose.api.yaml          - Expose Ollama API port
# docker-compose.otel.yaml         - Grafana OTel observability
# docker-compose.playwright.yaml   - Playwright for web scraping
```
# ⚠️  NEVER run Docker commands here for testing. This is the development machine only.

### Tests
```bash
# Python tests (pytest, requires dev dependencies):
python -m pytest backend/open_webui/test/ -v
# Run with async support (pytest-asyncio configured in pyproject.toml)
```
**Important:** Do **not** run Docker compose or `run-compose.sh` to test — use Python tests directly.

## Code Conventions & Patterns

### Python (`backend/open_webui/`)

- **Formatter**: Ruff (single quotes, line length 120), Black (line length 120, `skip-string-normalization = true`)
- **Linter**: Ruff with E/F/W/I/UP/C90/Q/ICN rules; max McCabe complexity 10; Google-style docstrings
- **Imports**: isort via Ruff; `ast` and `datetime` are banned from explicit import; use `import datetime as dt`
- **Typing**: Type hints on function signatures; Pydantic v2 for request/response models
- **DB**: SQLAlchemy 2.0 async (`async def`), `SessionLocal` injected via FastAPI `Depends()`
- **Error handling**: Raise specific exceptions; routers return Pydantic model responses or `JSONResponse`
- **Config**: Use `config.py`'s `get_config_val()` for environment variable access with typed defaults

### Frontend (`src/`)

- **Framework**: Svelte 5 with runes syntax (`$state`, `$derived`, `$effect`)
- **TypeScript**: Strict mode via `tsconfig.json` (extends `.svelte-kit/tsconfig.json`)
- **Styling**: Tailwind CSS 4 + custom CSS; SCSS via `sass-embedded`
- **Linting**: ESLint with `@typescript-eslint`, `eslint-plugin-svelte`, `eslint-plugin-cypress`
- **Formatting**: Prettier (tabs, single quotes, 100 char width) + `prettier-plugin-svelte`

### Naming

- Python modules: `snake_case`
- Classes/Enums: `PascalCase`
- Pydantic models: `ModelName`, `ModelNameCreate`, `ModelNameUpdate`, `ModelNameResponse`
- Frontend components: `FileName.svelte` (PascalCase in filenames)

## Important Files

| File | Purpose |
|---|---|
| `backend/open_webui/main.py` | FastAPI app, middleware stack, router mounting, SPA fallback |
| `backend/open_webui/env.py` | All runtime env vars, device detection, JSON logging config |
| `backend/open_webui/config.py` | Persistent config singleton, DB config table, Alembic setup |
| `backend/open_webui/__init__.py` | Typer CLI entry point (`serve`, `dev`) |
| `backend/open_webui/utils/chat.py` | Chat completion pipeline (RAG, tool calling, streaming) |
| `backend/open_webui/utils/auth.py` | JWT ops, password hashing, user auth dependencies |
| `backend/open_webui/utils/oauth.py` | OAuth/OpenID Connect manager, authlib integration |
| `backend/open_webui/utils/plugin.py` | Dynamic function/tool loader (disk + GitHub Gist) |
| `pyproject.toml` | Python deps (hatchling build), ruff/black/codespell config |
| `package.json` | Frontend deps, scripts, Node 22 required |
| `Dockerfile` | Multi-stage: Node 22 frontend → Python 3.11 backend |
| `docker-compose.yaml` | Default compose (ollama + open-webui) |
| `.github/workflows/docker-build.yaml` | CI: multi-arch Docker images (main/cuda/slim/ollama) |

## Runtime & Tooling

- **Node.js**: 22 (required by frontend build)
- **Python**: 3.11 or 3.12 only (enforced in `pyproject.toml`)
- **Package managers**: `npm` (frontend), `uv` (backend lockfile via `uv.lock`), `pip` acceptable for dev
- **Database**: SQLite (default, `aiosqlite`), PostgreSQL with `pgvector` (production)
- **Build**: `hatchling` (Python), Vite 5 + SvelteKit (frontend)
- **Migrations**: Alembic (`backend/alembic.ini`)

## Testing & QA

### Python Tests
- **Framework**: `pytest` (v8.3), `pytest-asyncio`, `pytest-docker`
- **Location**: `backend/open_webui/test/`
- **Organization**: `util/` (standalone unit tests), `apps/webui/routers/` (integration tests), `apps/webui/storage/` (provider tests)
- **Mocking**: `moto` (S3), `gcp-storage-emulator`, `@patch`, `monkeypatch`, `tmp_path`
- **Run**: `python -m pytest backend/open_webui/test/ -v`

### Frontend Tests
- **Vitest** is in `devDependencies` (`^1.6.1`) with script `npm run test:frontend`
- **Cypress** is installed (`^13.15.0`) for E2E testing (`npm run cy:open`)
- Currently no visible frontend test files in `src/`

### Linting & Type Checking
- **Python**: `ruff check` (E/F/W/I/UP/C90/Q/ICN), `ruff format`, `black`, `pylint backend/`, `codespell`
- **Frontend**: `eslint . --fix`, `svelte-check`, `prettier --write`
- **All-in-one**: `npm run lint` (runs frontend, types, and backend lint)

## Docker Image Variants

The CI pipeline (`.github/workflows/docker-build.yaml`) builds five variants:
- `main` — default (Ollama + Open WebUI)
- `cuda` — NVIDIA CUDA support
- `cuda126` — CUDA 12.6 specific
- `ollama` — bundled Ollama runtime
- `slim` — minimal image without Ollama

Build args: `USE_CUDA`, `USE_OLLAMA`, `USE_SLIM`, `USE_PERMISSION_HARDENING`, `EMBEDDING_MODEL`, `RERANKING_MODEL`.
