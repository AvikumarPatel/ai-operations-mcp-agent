# MCP Guide

## Server role

The MCP server is an adapter between Codex and the FastAPI business API. It does not bypass the API or manipulate SQLite directly.

## Read tools

| Tool | Purpose |
|---|---|
| `search_products` | Search products by category and maximum price |
| `get_product_details` | Retrieve product details by SKU |
| `check_inventory` | Retrieve warehouse inventory by SKU |
| `get_quote` | Retrieve an existing quote |
| `get_support_ticket` | Retrieve an existing support ticket |

## Guarded write tools

| Prepare tool | Execute tool | Result |
|---|---|---|
| `prepare_quote_draft` | `create_quote_draft` | Draft quote |
| `prepare_support_ticket` | `create_support_ticket` | Open support ticket |

Prepare tools validate input and return a summary plus a confirmation token. Execute tools consume that token.

## Token properties

- short-lived
- single-use
- action-specific
- generated server-side
- cannot be guessed or reconstructed by the model

## Inspector

Run:

```bash
mcp dev mcp_server/server.py
```

The final validated server exposes **9 tools**.

## Codex behavior

`AGENTS.md` instructs Codex to:

- use the MCP tools as the source of truth
- avoid inventing SKUs, prices, inventory, quote status, or ticket status
- use the minimum read tools needed
- present prepared write summaries before execution
- require explicit confirmation before calling final create tools
- never write directly to the database to satisfy a business request
