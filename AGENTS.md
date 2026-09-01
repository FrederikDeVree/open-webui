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

## LOCAL (dev-arvoo) CUSTOM CHANGES

This branch (`dev-arvoo-v0.11.1`, merged with upstream/dev at v0.11.1, merge commit `db877818c`) carries the
following local changes on top of upstream.
Identify them by author `frederik@arvoo.com`. The big bundle is the consolidation commit `d2a8e93bc`
("dev-arvoo: consolidate changes on clean origin/dev base"); the rest are individual feature/fix commits.
When merging upstream, preserve these unless explicitly superseded (see status notes).

### 1. Terminal file access & downloads (user feature)
Let the user browse/download files from connected terminal servers, and make model-produced file paths clickable.
- `src/lib/utils/terminal.ts` (new file) — `TERMINAL_DOWNLOAD_SCHEME` (`terminal-download://`), `TERMINAL_PATH_RE`
	(absolute POSIX path + extension), `downloadTerminalFile()` (downloads via `downloadFileBlob` from the selected terminal).
- `src/lib/components/chat/Messages/Markdown/MarkdownInlineTokens.svelte` + `.../MarkdownInlineTokens/CodespanToken.svelte` —
	intercept `terminal-download://` links and terminal-path code spans, render as clickable download buttons.
- `src/lib/components/chat/FileNav.svelte` + `FileNav/FileNavToolbar.svelte` — per-terminal **home directory** clamping:
	`homePath` + `clampToHome()` keep navigation below the terminal's home; breadcrumbs built from `homePath`;
	home re-detected via `getCwd` on terminal switch.
- `src/routes/+layout.svelte` — terminal server mapping (proxy URL + session key for FileNav browsing).
- `backend/open_webui/routers/terminals.py`, `backend/open_webui/utils/terminals.py` — terminal proxy/context utilities.
- **Status:** the "clickable markdown path" part (`terminal-download://` + `TERMINAL_PATH_RE` + `downloadTerminalFile`
	+ the two Markdown token files) **coexists with** upstream's `display_file` tool (upstream 0.11.1: `TerminalOutputFile.svelte`,
	`terminalFileDisplay` setting, `terminal:display_file` socket event). Upstream's inline `display_file` card is NOT a good
	replacement for clickable paths in plain markdown, so **both are kept**. **Done after the v0.11.1 merge (2026-08-28)**:
	the clickable-path code was re-added to `MarkdownInlineTokens.svelte` (terminal scheme + terminal-server-origin path
	interception in `handleLinkClick` + `isTerminalDownload` branch) and `CodespanToken.svelte` (`isTerminalPath`/`isPyodidePath`
	branches), merged with upstream's `chatFadeStreamingText` fade, `underline` token and `allowExternal` image support.
	`src/lib/utils/terminal.ts` is **in use again — do not delete**. The `FileNav` `homePath`/`clampToHome` clamping and the
	terminal proxy utils also remain local and should be kept.

### 2. Send message while attachments upload (user feature — SUPERSEDED)
Block-and-wait: while non-image files are still `uploading`, the send handler polls until they finish.
- `src/lib/components/chat/Chat.svelte` — `let awaitingUpload = false;` + a 100 ms polling block in the send handler;
	passes `uploadPending={awaitingUpload}` to `MessageInput` (two instances).
- `src/lib/components/chat/MessageInput.svelte` — `export let uploadPending = false;`; send button disabled + spinner +
	"Waiting for upload..." tooltip while `uploadPending`.
- **Status:** **superseded by upstream's queue** (`chatRequestQueues` store, `processNextInQueue`, `QueuedMessageItem.svelte`,
	`messageQueue` prop). Decision: **drop this, use upstream's queue.** **Done in the v0.11.1 merge**: `Chat.svelte` is the
	upstream version (queue-based `uploadPending`, no `awaitingUpload` polling).

### 3. Mermaid / Vega diagram rendering (user feature)
Client-side diagram rendering with SVG→PNG rasterization for LLM visual feedback and self-correction.
- `src/lib/utils/index.ts` — `initMermaid` (native SVG `<text>` labels via `htmlLabels:false`, `wrappingWidth`),
	`renderMermaidDiagram` (off-screen 1100px container so gantt charts read a real width),
	`convertForeignObjectsToSvgText` (foreignObject→`<text>` so labels survive PNG), `svgToPng` (data-URI canvas, untainted).
- `src/routes/+layout.svelte` — `executeDiagram` handler for the `execute:diagram` socket event (mermaid/vega/vega-lite → svg+png).
- `backend/open_webui/utils/middleware.py` — `open_webui:diagram_renderer` output type + a diagram-renderer loop that scans
	accumulated content for mermaid/vega/vega-lite blocks and feeds errors/PNG back to the model.
- `src/lib/components/chat/Messages/Markdown.svelte`, `MarkdownTokens.svelte`, `ConsecutiveDetailsGroup.svelte`,
	`ResponseMessage.svelte` — render the diagram blocks.

### 4. Pyodide file downloads (user feature)
- `src/lib/utils/pyodide.ts` (new file) — `sendPyodideWorkerMessage`, `downloadPyodideFile`, `PYODIDE_DOWNLOAD_SCHEME`
	(`pyodide-download://`), `linkifyPyodidePaths` (turns bare `/mnt/uploads/...` paths into download links, skipping code spans).
- `src/lib/components/chat/Messages/Markdown.svelte` / markdown pipeline — consumes the pyodide download scheme.

### 5. Multiple LDAP servers (user feature)
Authenticate against a list of LDAP servers (continue-on-failure) instead of a single one.
- `backend/open_webui/config.py` — `ldap_servers` config (list).
- `backend/open_webui/routers/auths.py` — `ldap_auth` loops over all configured servers (continue instead of break on failure).
- `backend/open_webui/migrations/versions/4a1b2c3d4e5f_add_ldap_servers_config.py` — migration.
- `backend/tests/test_ldap_servers.py` — tests.
- `src/lib/apis/auths/index.ts`, `src/lib/components/admin/Settings/Authentication.svelte` — admin UI for multiple servers.
- **Status:** upstream 0.11.1 refactored `auths.py` (single-server flow + group creation + SSO events). The local `ldap_auth`
	is a **superset** — it already includes upstream's group-creation/event code wrapped in the multi-server loop. Keep the local version.

### 6. Per-knowledge-base full-context retrieval toggle (user feature)
Per-KB toggle to default file attachments to full-context retrieval mode.
- `backend/open_webui/models/knowledge.py` — `context` field on `KnowledgeForm` (excluded from update in KnowledgeTable).
- `backend/open_webui/retrieval/utils.py`, `backend/open_webui/routers/knowledge.py` — retrieval plumbing.
- `src/lib/apis/knowledge/index.ts`, `src/lib/components/workspace/Knowledge/KnowledgeBase.svelte`,
	`src/lib/components/workspace/Models/Knowledge.svelte`, `.../Knowledge/KnowledgeSelector.svelte` — UI toggle.

### 7. RAG_FILE_FULL_CONTEXT default (user feature)
Global config to default file attachments to full-context mode.
- `backend/open_webui/config.py` — `RAG_FILE_FULL_CONTEXT`.
- `backend/open_webui/routers/retrieval.py`, `backend/open_webui/utils/middleware.py` — apply it.
- `src/lib/components/admin/Settings/Documents.svelte`, `src/lib/components/common/FileItemModal.svelte`,
	`src/lib/stores/index.ts` — admin toggle + reactive `$config` usage.

### 8. Builtin knowledge tool rename + default counts (user feature)
- `backend/open_webui/tools/builtin.py`, `backend/open_webui/utils/middleware.py`, `backend/open_webui/utils/tools.py` —
	renamed `query_knowledge_files` → `search_knowledge_files` + `list_knowledge_files`.
- Default counts: `search_knowledge_files` count 50, default query count 10 (`backend/open_webui/tools/builtin.py`).
- **Status:** upstream kept the old name. Preserve the local rename consistently across all references.
- **Verified in the v0.11.1 merge**: zero `query_knowledge_files` references remain in `backend/` and `src/`.

### 9. Per-request embedding cache (user feature)
- `backend/open_webui/retrieval/utils.py`, `backend/open_webui/routers/retrieval.py` — `request.state.embedding_cache`
	to avoid redundant embedding generation within a request (passed as `cache=` to the embed call).

### 10. External Qdrant hybrid search (dense + BM25 sparse via fastembed) (user feature)
Let an **external Qdrant knowledge base** do hybrid search: dense vector + BM25 sparse, fused in Qdrant via RRF.
The external collection is **pre-existing** (managed outside Open WebUI) and must **already contain a named
sparse (BM25) vector** built with the same fastembed tokenizer (`Qdrant/bm25`) for hybrid search to work.
Opt-in per source via a `sparse_field` config key; if unset, retrieval is unchanged (dense-only).
- `backend/open_webui/retrieval/external.py` — `_get_bm25_model()` (lazy cached `SparseTextEmbedding('Qdrant/bm25')`),
	`_bm25_sparse_vector(query)` → `models.SparseVector`, and `_retrieve_qdrant` builds a hybrid `query_points`
	(two `models.Prefetch`: dense `using=vector_field` + sparse `using=sparse_field`, each `limit=max(count*10,100)`,
	fused with `models.FusionQuery(fusion=models.Fusion.RRF)`). RRF fused scores are small positive values (not cosine
	`[0,1]`); no threshold is applied in the external path so no normalization is needed.
- `backend/open_webui/routers/knowledge.py` — `_get_normalized_external_source` adds `sparse_field` to `allowed_keys`
	for the `qdrant` provider (optional).
- `src/lib/components/admin/Settings/ExternalKnowledge.svelte` — `sparseField` form field (qdrant-only input + tooltip),
	wired into `sourceForm`/`schemaDefaults`/`openEditSource`/`sourcePayload`.
- `src/lib/i18n/locales/en-US/translation.json` — "Sparse (BM25) Field" + tooltip string.
- **Dependency:** `fastembed==0.7.4` added to `pyproject.toml` `[all]` (next to `qdrant-client`) and
	`backend/requirements.txt`. fastembed requires `pillow<12.0` (py3.10–3.13), so installing `[all]` downgrades the
	base `pillow==12.2.0` pin to 11.x (the project's basic PIL usage — `Image`/`ImageOps` — is unaffected). The base
	install (without `[all]`) keeps pillow 12.2.0. fastembed is lazy-imported only when hybrid search is enabled.
- **Indexing-side alignment (critical):** the sparse vector in the external collection is built by a separate
	indexing pipeline (outside this repo). Keep **both sides on fastembed `Bm25` defaults**
	(`language="english"`, `k=1.2`, `b=0.75`, `avg_len=256.0`) and **pin the same fastembed major version** on both
	sides so the tokenizer stays identical. Only the tokenizer (`language`/stemmer/`token_max_length`) must actually
	match — `k`/`b`/`avg_len` only shape the stored document weights on the indexing side; the query side hashes tokens
	with weight 1.0 and never uses them. `SparseTextEmbedding('Qdrant/bm25')` wraps a `Bm25` with exactly these
	defaults (verified in fastembed 0.7.4). If the indexing side is ever upgraded, re-verify the tokenizer matches.
- **Status:** local-only; preserve on the next upstream merge. **Verify after a merge** (quick greps):
	`_bm25_sparse_vector` + `sparse_field` in `external.py`; `sparse_field` in `knowledge.py`; `sparseField` in
	`ExternalKnowledge.svelte`; `fastembed==0.7.4` in `pyproject.toml` + `requirements.txt`.

### 11. Misc local fixes
- `src/lib/components/layout/ChatsModal.svelte` — use `copyToClipboard` utility instead of `navigator.clipboard`.
- `Dockerfile` — increase Node.js heap size to avoid OOM during build.
- `docker-compose.dev-arvoo.yaml` — dev-specific postgres + volumes, vector DB, login form enabled in dev, port fixes.
- `docker-compose.arvoo.yaml` — RAG embedding support for non-dev container.
- `backend/open_webui/migrations/versions/1ff6ce645...` — Alembic migration to merge DB heads.
- `AGENTS.md` — this knowledge base file.

### Merge notes (upstream/dev → 0.11.1)
**Completed 2026-08-26** (merge commit `db877818c` on `dev-arvoo-v0.11.1`; 320 conflicts).
- **Take upstream** for: `aiodns` (upstream pins 3.6.1; local had 4.0.4 — use upstream, opt-in via `AIOHTTP_CLIENT_ASYNC_DNS_RESOLVER`),
	`utils/timers.py` (column-based `Chat.timer_at`, fixes #27663), the moved/refactored model-normalization + context-usage block in
	`Chat.svelte` (upstream moved it; a new copy using `getUsageTokenCount` sits just below the old location), and all px→rem unit
	conversions (upstream's "Interface scaling" work).
- **Drop** local test deps `moto[s3]`, `docker`, `pytest`, `pytest-docker` from `pyproject.toml` `[all]` and `uv.lock`.
- **Keep** local: items 1 (clickable terminal paths + FileNav home-path + terminal proxy), 3, 4, 5, 6, 7, 8, 9, 10, 11.

### Merge mechanics (gotchas for the next upstream merge)
- **`git checkout --theirs <many paths>` is atomic**: if even one path has no "theirs" stage (e.g. a delete/modify `UD` conflict),
	the whole command fails and **nothing** is checked out. A subsequent `git add` then stages the working tree as-is — which may
	still contain conflict markers, and `git diff --diff-filter=U` shows 0 (the index looks merged). To force a file to the
	upstream blob regardless of stage state, use `git checkout MERGE_HEAD -- <file>` instead.
- **Upstream is a superset in several places** — no re-apply needed: `(app)/+layout.svelte` terminal-server mapping (proxy URL +
	session key for FileNav), `Chat.svelte` `displayFileHandler`/queue-based `uploadPending`, FileNav bulk selection +
	folder upload + `$terminalServers === null` loading guards.
- **Local-only files to preserve** (not in upstream, easy to lose): `src/lib/utils/pyodide.ts`, `src/lib/utils/terminal.ts`
	(delete once item 1 is fully dropped), `AGENTS.md`, the two local Alembic migrations
	(`4a1b2c3d4e5f_add_ldap_servers_config.py`, `merge_heads_4a1b2c_f0bd01.py`,
	`merge_heads_5f6a7b_d4c1a8.py` — merges upstream's `d4c1a8e37b62` (chat `timer_at`) with local `5f6a7b8c9d0e`,
	added 2026-08-26 after the v0.11.1 merge created two heads), `backend/tests/test_ldap_servers.py`,
	`docker-compose.arvoo.yaml` / `docker-compose.dev-arvoo.yaml`, `backup-postgres.sh` / `restore-postgres.sh`.
- **Verify after a merge** (quick greps): `homePath` in `FileNav.svelte`; `LDAP_SERVERS` in `Authentication.svelte` +
	`/admin/config/ldap/servers` in `auths.py`; `RAG_FILE_FULL_CONTEXT` in `config.py` + `Documents.svelte`; `kbFullContext` in
	`KnowledgeBase.svelte`; `diagram_renderer` in `middleware.py` + `MarkdownTokens.svelte`; `linkifyPyodidePaths` in
	`Markdown.svelte`; `toggleTerminal` in `TerminalMenu.svelte`; `search_knowledge_files` (and 0× `query_knowledge_files`)
	in `tools/builtin.py`.
