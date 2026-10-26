# Security

This repository is a portfolio demonstration using fictional data. It is not intended to expose production credentials, customer information, or production infrastructure.

## Do not commit

- `.env`
- API keys, OAuth tokens, passwords, or secrets
- local SQLite databases (`*.db`, `*.sqlite`, `*.sqlite3`)
- virtual environments
- raw evaluation traces
- generated coverage reports
- real customer or employee information

## Agent write controls

State-changing MCP operations use a two-step flow:

1. `prepare_*` validates the request and creates a short-lived confirmation token.
2. The user reviews the summary and explicitly confirms.
3. `create_*` consumes the token and performs the write.

Tokens are single-use, action-bound, and time-limited. A quote token cannot authorize a support ticket, and a consumed token cannot be replayed.

## Tool behavior

Read tools are marked read-only. Write tools are marked state-changing and should remain subject to host-level approval policies. Tool annotations are hints for clients; they are not a substitute for server-side validation and confirmation.

## Data handling

The repository uses fictional sample products, customers, inventory, quotes, and support tickets. Replace sample data with an appropriately secured data source before any real deployment.

## Reporting

If you find a security issue in this portfolio repository, open a GitHub issue without including secrets or sensitive data.
