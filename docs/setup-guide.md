# Setup Guide

## Prerequisites

- Python 3.11+ (project validated with Python 3.13)
- Git
- Node.js / npm / npx for MCP Inspector
- `uv` for the MCP development launcher
- OpenAI Codex CLI for the final agent workflow

## Python environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment configuration

Copy `.env.example` to `.env`.

Example local values:

```env
APP_ENV=development
API_BASE_URL=http://127.0.0.1:8000
WEBHOOK_URL=http://127.0.0.1:8000/webhooks/activity
```

Never commit `.env`.

## Seed sample data

```bash
python -m app.seed
```

The seed script uses fictional products, inventory, and customers.

## Start the API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

## Run tests

```bash
python -m pytest -v
```

Coverage:

```bash
python -m pytest --cov=app --cov-report=term
```

## MCP Inspector

```bash
mcp dev mcp_server/server.py
```

If `npx` is missing, install Node.js. If `uv` is missing, install `uv` and ensure it is on PATH.

## Codex MCP registration

Register the local stdio server with the Python executable from the virtual environment:

```text
codex mcp add ai_operations -- <python-executable> <absolute-path-to-mcp_server/server.py>
```

Start Codex from the repository root and use `/mcp` to verify the server.

The repository-level `AGENTS.md` provides business-tool instructions and confirmation rules.
