# Local Electron Desktop Bundle Design

## Goal

Package ShopBot as a macOS desktop application that can be opened by an end user without installing Docker, Python, Node.js, or an IDE.

The app should include a working executable for academic submission and should be suitable for later Windows packaging from a Windows environment.

## Submission Context

The final code archive is expected to contain:

- an explanatory `readme.txt`
- the Maintenance Manual as a PDF
- all source code and necessary data files
- a working executable of the program

The archive should be arranged under a single top-level folder named `surname_forename`. The package should avoid unnecessary generated dependencies such as `node_modules`, virtual environments, Docker images, and build caches.

## Scope

This design covers a fully local desktop bundle:

- Electron desktop shell
- bundled React frontend
- bundled FastAPI backend
- bundled local n8n instance with visible workflow UI
- local SQLite product database
- first-run initialization and service supervision
- academic ZIP/TAR packaging guidance

This design does not cover cloud deployment, hosted model proxying, notarized public distribution, or an auto-update system.

## Chosen Approach

Use Electron as the desktop shell and process supervisor.

Electron loads the built React frontend from disk, starts the local FastAPI service, starts the local n8n service, and exposes a visible workflow view for inspecting or editing the local n8n workflow.

Runtime process graph:

```text
Electron app -> bundled React UI -> local FastAPI -> local n8n workflow
                                            |
                                            v
                                      local SQLite
```

The React chat UI should call only FastAPI. It should not call n8n directly. The workflow UI is visible for demonstration and inspection, but FastAPI remains the integration boundary for recommendation behavior.

## App Components

### Electron Main Process

Responsibilities:

- create the main application window
- load the bundled React frontend
- start and stop local child processes
- assign or validate localhost ports
- run startup health checks
- expose app status to the renderer through a narrow preload bridge
- provide navigation between `ShopBot` and `Workflow`
- handle app shutdown by terminating child processes cleanly

Security settings:

- keep `nodeIntegration` disabled
- keep `contextIsolation` enabled
- use a preload script for any desktop-only API exposed to the renderer

### React Renderer

Responsibilities:

- render the existing ShopBot chat UI
- stream responses from local FastAPI
- show service startup and service unavailable states
- preserve visible chat history when a network or local service error occurs
- provide a top-level navigation entry for the visible workflow view

The renderer should use a runtime API base URL supplied by Electron, not a build-time-only `VITE_API_URL`, because the local backend port may need to be controlled by the app.

### FastAPI Backend

Responsibilities:

- serve the existing `/chat` streaming endpoint
- keep model-provider API key handling server-side
- read products from the local SQLite database
- call the local n8n webhook for the recommendation pipeline
- provide any internal product-query endpoints required by the n8n workflow
- keep the existing fallback recommendation path when n8n is unavailable or returns invalid data

Packaging strategy:

- build the backend into a standalone executable with PyInstaller or an equivalent Python packager
- include `backend/app`, required Python dependencies, and runtime metadata
- pass runtime paths and ports through environment variables

### Local n8n

Responsibilities:

- run locally as a child process controlled by Electron
- expose the n8n editor UI inside the desktop app's `Workflow` view
- host the recommendation webhook used by FastAPI
- persist workflow state under the user's app data directory

Packaging strategy:

- bundle a known Node.js runtime with the app
- bundle the n8n package or an installed n8n runtime tree
- avoid depending on system Node.js or global npm packages

User-editable workflow state introduces recoverability requirements. The app should include a `Restore Default Workflow` action that re-imports `workflows/recommendation-pipeline.json` into the local n8n instance.

### SQLite Data

Responsibilities:

- provide the local product catalog used by the backend
- persist in a writable user data directory

The packaged app should include a seed copy of `data/products.db`. On first run, Electron should copy it to:

```text
~/Library/Application Support/ShopBot/products.db
```

FastAPI should receive `DATABASE_PATH` pointing to that writable copy. The app bundle itself should be treated as read-only.

## Runtime Flow

### First Launch

1. Electron creates the app data directory if it does not exist.
2. Electron copies the seed SQLite database into app data if missing.
3. Electron initializes the local n8n data directory if missing.
4. Electron starts n8n and waits for its health endpoint.
5. Electron imports the default workflow if the local n8n instance has no matching workflow.
6. Electron starts FastAPI with `DATABASE_PATH` and `N8N_WEBHOOK_URL` pointing to local resources.
7. Electron waits for FastAPI health.
8. The app enables the ShopBot UI and Workflow UI.

### Later Launches

1. Electron reuses the existing app data directory.
2. Electron starts n8n and FastAPI.
3. Electron verifies both health checks.
4. The app opens with the last persisted n8n workflow state intact.

### Shutdown

Electron should terminate child processes that it started. If a process exits unexpectedly while the app is running, the UI should show a service status state and offer retry.

## Ports

Default local ports:

- FastAPI: `127.0.0.1:8000`
- n8n: `127.0.0.1:5678`

If either port is unavailable, the app should detect the conflict and either choose an available port or show a clear startup error. The runtime API base URL and `N8N_WEBHOOK_URL` must be derived from the chosen ports.

For the first implementation, fixed ports are acceptable if startup errors are explicit. Dynamic ports are a later hardening step.

## Visible Workflow UI

The app should expose two top-level views:

- `ShopBot`: bundled React chat UI
- `Workflow`: local n8n editor UI

The Workflow view can be implemented as a second Electron `BrowserWindow` or as a routed view containing the local n8n URL. A second window is safer for isolation and avoids mixing the React app route space with n8n route handling.

The n8n editor is intended for demonstration and inspection. Because edited workflows can break the recommendation path, the app should provide a restore action and should keep FastAPI's existing fallback behavior.

## Environment and Secrets

The app still requires an Anthropic API key unless the backend is later changed to use another model provider or a hosted proxy.

For an academic executable, acceptable options are:

- read `ANTHROPIC_API_KEY` from a local settings screen and store it in the OS keychain
- read `ANTHROPIC_API_KEY` from a local `.env` file placed next to the executable for demonstration

The preferred product approach is keychain storage. A `.env` file is simpler for a submission demo but should be documented clearly in `readme.txt`.

No API key should be hard-coded into source code or committed to the archive.

## Expected Size

The repository's source and data are small, but the desktop bundle is dominated by runtimes:

- Electron Chromium runtime
- bundled Python backend executable
- bundled Node.js runtime
- bundled n8n runtime and dependencies

Expected macOS `.app` size: roughly 450 MB to 900 MB.

Separate `arm64` and `x64` builds should be produced instead of a universal binary during the first implementation to keep package size lower.

## Archive Layout

Target archive shape:

```text
surname_forename/
  readme.txt
  MaintenanceManual.pdf
  executable/
    ShopBot.app
  source/
    backend/
    data/
    docker/
    docs/
    frontend/
    workflows/
    package files and build scripts
```

The archive should include source files and necessary data files, but should exclude:

- `.git/`
- `node_modules/`
- Python virtual environments
- build caches
- Docker images
- local n8n runtime data generated during testing
- secrets such as `.env` with real API keys

If the executable requires a demo `.env`, include a template or explain the required variable in `readme.txt`.

## readme.txt Requirements

The submission `readme.txt` should summarize:

- archive contents
- supported operating system for the included executable
- hardware and software dependencies
- how to run the included executable
- how to compile the app from source
- how to provide `ANTHROPIC_API_KEY`
- how to reset the local workflow if edited
- expected first-run startup time

For the fully local macOS executable, the dependency list should say that end users do not need Docker, Python, Node.js, or an IDE to run the included app. Developers compiling from source still need Node.js, Python, and the packaging toolchain.

## Build Strategy

Initial macOS build steps:

1. Build the React frontend with Vite.
2. Package the FastAPI backend as a standalone local executable.
3. Prepare the bundled Node.js and n8n runtime.
4. Add Electron main and preload code to start and supervise local services.
5. Package the app with an Electron packager such as `electron-builder`.
6. Verify the `.app` on a clean macOS user account or unpacked temporary directory.

Windows should be built later on a Windows environment using the same architecture, with platform-specific paths and process handling.

## Testing Strategy

### Local Development

- run existing backend tests
- run existing frontend tests
- run the Docker stack only as a comparison environment, not as the desktop runtime

### Packaged App

- launch the packaged `.app`
- confirm the ShopBot view loads
- confirm FastAPI health succeeds
- confirm n8n health succeeds
- confirm the Workflow view opens the local n8n editor
- send a chat message that triggers recommendations
- quit and relaunch to confirm persisted app data still works
- edit or disable the workflow and verify restore behavior
- unpack the final archive in another folder and verify it still contains the required files

## Risks

- Bundling n8n without Docker may be brittle because n8n expects a Node.js runtime and persistent writable state.
- First launch may be slow while n8n initializes.
- Port conflicts can block startup if fixed ports are used.
- User-edited n8n workflows can break tested recommendation behavior.
- Unsigned macOS apps can trigger Gatekeeper friction on other machines.
- Including all runtimes may make the executable large for academic upload limits.

## Success Criteria

- A user can open `ShopBot.app` on macOS without installing Docker, Python, Node.js, or an IDE.
- The app starts local FastAPI and local n8n automatically.
- The ShopBot chat UI can produce recommendations using the local SQLite database.
- The Workflow view exposes the local n8n editor.
- The app can recover from a modified workflow by restoring the default workflow.
- The final ZIP/TAR contains `readme.txt`, the Maintenance Manual PDF, source code, required data, and a working executable under `surname_forename`.
