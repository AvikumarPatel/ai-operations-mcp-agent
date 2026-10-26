# Security and Guardrails

## Source-of-truth rule

Codex is instructed to use MCP tools for business facts. It should not invent prices, stock quantities, SKUs, quote status, or support-ticket status.

## Controlled failures

Expected business errors are converted to readable MCP tool errors. For example, an unknown SKU returns a controlled not-found result rather than a Python traceback or fabricated quantity.

## Write separation

Writes use two tools rather than one:

```text
prepare action → user reviews summary → explicit confirmation → create action
```

This makes the intended business effect visible before state changes.

## Confirmation tokens

Tokens are:

- short-lived
- consumed on first use
- bound to one action type
- generated with secure randomness

A reused or mismatched token is rejected.

## Host + server controls

The design combines host-level write approval behavior with server-side confirmation and validation. Host annotations alone are not treated as authorization.

## Persistence boundary

MCP tools call the FastAPI service rather than manipulating SQLite directly. Business rules therefore remain centralized in the API layer.

## Auditability

State-changing operations create activity records. Webhook delivery success and failure are also logged.

## Repository hygiene

The public repository should exclude:

- `.env`
- `*.db`, `*.sqlite`, `*.sqlite3`
- `.venv/`
- `.pytest_cache/`
- `.coverage*`
- `htmlcov/`
- `evals/artifacts/`
- `.vscode/`
