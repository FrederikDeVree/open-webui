# PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-02

## OVERVIEW

Project: **Open WebUI** — A feature-rich, open-source AI-powered web UI for running multimodal LLM applications locally.
Stack: **Svelte 5 + SvelteKit + Vite (frontend)**, **FastAPI + SQLAlchemy + Pydantic (backend)**, **Docker (deployment)**, Node.js 22 / Python 3.11-3.12
License: Proprietary

## STRUCTURE

```
open-webui/
├── src/                    # Frontend SvelteKit application
│   ├── lib/                # Shared library code
│   │   ├── components/     # Svelte components (chat, admin, app, icons, etc.)
│   │   ├── apis/           # API client functions organized by domain
│   │   ├── stores/         # Svelte writable stores (state management)
│   │   ├── utils/          # Utility functions (formatting, markdown, etc.)
│   │   ├── types/          # TypeScript type definitions
│   │   ├── constants/      # Shared constants
│   │   └── workers/        # Web workers (pyodide)
│   └── routes/             # SvelteKit pages + layouts (app, auth, admin)
├── backend/                # Python backend
│   ├── open_webui/         # Main backend package
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── routers/        # Route handlers (chats, users, tools, etc.)
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── utils/          # Backend utilities (auth, middleware, etc.)
│   │   ├── storage/        # File storage abstraction
│   │   ├── retrieval/      # RAG/vector search infrastructure
│   │   ├── tools/          # MCP tools integration
│   │   ├── socket/         # WebSocket handlers
│   │   ├── tasks.py        # Background tasks (APScheduler)
│   │   └── migrations/     # Database migrations (alembic)
│   └── requirements.txt    # Python dependencies
├── docs/                   # Documentation (security policy, etc.)
├── cypress/                # End-to-end tests (Cypress)
├── test/                   # Additional test files
├── tools/                  # Contributed tools (e.g., little-coder)
├── scripts/                # Build/dev scripts
└── .svelte-kit/            # SvelteKit generated types
```

## COMMANDS

| Action               | Command                                                      |
| -------------------- | ------------------------------------------------------------ |
| Install (frontend)   | `npm ci --force`                                             |
| Install (backend)    | `uv pip install -r backend/requirements.txt`                 |
| Test (frontend)      | `npm run test:frontend` (runs vitest)                        |
| Test (e2e)           | `npm run cy:open` (Cypress)                                  |
| Build                | `npm run build` (builds frontend + pyodide assets)           |
| Run (dev)            | `npm run dev` (watches and serves frontend)                  |
| Run (backend)        | `bash backend/start.sh` (uvicorn, auto-generates secret key) |
| Run (standalone dev) | `bash run.sh` (Docker build + run)                           |
| Run (docker-compose) | `make startAndBuild` or `docker compose up -d`               |
| Lint                 | `npm run lint` (frontend + types + backend pylint)           |
| Format (frontend)    | `npm run format` (Prettier)                                  |
| Format (backend)     | `npm run format:backend` (ruff format)                       |
| i18n                 | `npm run i18n:parse`                                         |
| Check types          | `npm run check` (svelte-kit sync + svelte-check)             |

## CODING STANDARDS

### Frontend (TypeScript / Svelte 5)

- **Framework**: SvelteKit with Vite, adapter-static deployment
- **Language**: TypeScript (strict mode), svelte-check for type validation
- **Styling**: Tailwind CSS v4 (with typography + container-queries plugins) + custom CSS in `src/app.css`
- **State Management**: Svelte stores (`writable`, `derived`, `spring`)
- **Components**: Svelte 5 syntax (runes: `onMount`, `tick`, `getContext`); TypeScript scripts
- **Icons**: Custom icon components in `$lib/components/icons/`
- **Formatting**: Prettier (single quotes, tabs, 100 char width, LF endings), `prettier-plugin-svelte` for `.svelte` files
- **Linting**: ESLint (`@typescript-eslint`, `plugin:svelte`, `plugin:cypress`), Prettier integration
- **API Client**: Organized domain-by-domain in `$lib/apis/` (chats, users, tools, etc.)
- **Internationalization**: i18next with `$lib/i18n/` directory

### Backend (Python 3.11+)

- **Framework**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.x with Alembic migrations; also supports Peewee for some models
- **Database**: SQLite (default), PostgreSQL (optional via `psycopg`), Redis (sessions/caching)
- **Validation**: Pydantic v2
- **Auth**: JWT (python-jose), OAuth2 (authlib), session management (starsessions)
- **Styling**: Ruff (line length 120, single quotes, google docstrings, max cyclomatic complexity 10), black (secondary)
- **Testing**: pytest (with asyncio, docker fixtures), pylint
- **Pre-commit**: ruff check + ruff format on `backend/`
- **Storage**: Abstraction layer supporting local filesystem, S3, Azure Blob, GCP Storage
- **RAG**: ChromaDB, OpenSearch, Qdrant, Weaviate, Milvus, Pinecone, OracleDB supported
- **LLM Providers**: OpenAI, Anthropic, Google GenAI via LangChain

## WHERE TO LOOK

- **Frontend source**: `src/`
- **Backend source**: `backend/open_webui/`
- **Backend tests**: `backend/open_webui/test/`
- **Frontend E2E tests**: `cypress/e2e/`
- **Docs**: `docs/` (security), `docs/` folder at root
- **Docker**: `Dockerfile`, `docker-compose.yaml`, `docker-compose.*.yaml` variants
- **CI/CD**: `.github/workflows/` (build, format, lint, release)
- **i18n config**: `i18next-parser.config.ts`

## NOTES

- The project uses **hatchling** as the Python build system, with version sourced from `package.json`
- Frontend assets are built as a static site and served by the FastAPI backend at `backend/open_webui/static/`
- Pyodide (Python in browser) is used for client-side Python execution; fetched via `npm run pyodide:fetch`
- Git revision is baked into the build version at compile time
- Docker Compose supports multiple profiles: CUDA (GPU), Ollama embedding, SCIM, ArgoCD
- The backend auto-generates a `.webui_secret_key` if not provided via env var
- **Important**: Embedding model changes require re-embedding documents (RAG compatibility note in Dockerfile)
- Pre-commit hooks only lint/format backend Python (ruff); frontend uses npm scripts
- Tailwind CSS v4 uses a new configuration approach (PostCSS plugin instead of `tailwind.config.js` for some features, though a legacy config still exists)
