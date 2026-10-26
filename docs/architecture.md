# Architecture

## Overview

The project separates natural-language reasoning, tool execution, business validation, persistence, and event delivery into distinct layers.

```mermaid
flowchart TD
    U[User] --> C[OpenAI Codex]
    C -->|MCP| M[MCP Server]
    M -->|HTTP| F[FastAPI]
    F --> V[Validation / Business Rules]
    V --> D[(SQLite)]
    F --> L[Activity Log]
    F --> B[Background Webhook Task]
    B --> W[Webhook Receiver / External Automation]
```

## Read path

```mermaid
sequenceDiagram
    participant U as User
    participant C as Codex
    participant M as MCP Server
    participant A as FastAPI
    participant D as SQLite

    U->>C: Natural-language question
    C->>M: Select read tool
    M->>A: GET request
    A->>D: Query business data
    D-->>A: Record(s)
    A-->>M: JSON response
    M-->>C: Tool result
    C-->>U: Grounded answer
```

## Guarded write path

```mermaid
sequenceDiagram
    participant U as User
    participant C as Codex
    participant M as MCP Server
    participant A as FastAPI
    participant D as SQLite

    U->>C: Request quote/ticket
    C->>M: prepare_* tool
    M->>A: Validate product/inventory as needed
    A-->>M: Business data
    M-->>C: Summary + short-lived token
    C-->>U: Ask for explicit confirmation
    U->>C: Confirm
    C->>M: create_* with token
    M->>M: Consume token (single-use/action-bound)
    M->>A: POST write request
    A->>D: Persist record + audit event
    A-->>M: Created record
    M-->>C: Success result
    C-->>U: Created ID/status
```

## Design choices

- **FastAPI remains the business-system boundary.** MCP does not write directly to SQLite.
- **MCP is an adapter layer.** It translates model tool calls into validated REST operations.
- **Writes are intentionally two-step.** Preparation and execution are separate tools.
- **Audit events are first-class data.** Quote and support-ticket writes are traceable.
- **Webhook failures are isolated.** A delivery failure does not roll back a successful primary transaction.
- **Tests use an isolated SQLite database.** The real local database is not modified by regression tests.
