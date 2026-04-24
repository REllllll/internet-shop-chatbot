ShopBot Desktop Submission

Archive contents
- executable/ShopBot.app: macOS desktop executable bundle.
- source/: project source code, product database seed data, workflow export, and build scripts.
- MaintenanceManual.pdf: maintenance manual supplied with the submission archive.

Supported operating system
- The included executable is built for macOS on the architecture used by the packaging machine.
- End users running the included executable do not need Docker, Python, Node.js, npm, an IDE, or a database server.

Run the included executable
1. Open executable/ShopBot.app.
2. On first launch, allow the app time to initialize local services. First-run startup can take 30 to 90 seconds.
3. Provide ANTHROPIC_API_KEY through the local app data .env file if prompted by the demonstrator notes.

API key
- Do not hard-code an API key into source code.
- For the demo build, create a .env file in ~/Library/Application Support/ShopBot/ containing:
ANTHROPIC_API_KEY=your_key_here

Workflow reset
- Open ShopBot.
- Click Restore in the top bar to re-import the default recommendation workflow from workflows/recommendation-pipeline.json.

Compile from source
1. Install Node.js 20 or newer.
2. Install Python 3.12 or newer.
3. From the source folder, run python3 -m venv backend/.venv.
4. Run backend/.venv/bin/python -m pip install -r backend/requirements.txt.
5. Run npm install.
6. Run npm --prefix frontend install.
7. Place a macOS Node runtime under vendor/node.
8. Run bash scripts/prepare-n8n-runtime.sh.
9. Run npm run desktop:dist.

Expected local ports
- FastAPI: 127.0.0.1:8000
- n8n: 127.0.0.1:5678

If startup fails
- Check that ports 8000 and 5678 are not already in use.
- Close ShopBot and reopen it.
- Use Restore to reset the workflow if recommendations stop using the local n8n workflow.
