# Portfolio Wording

## Resume project entry

**AI Operations & Inventory Agent | Python, FastAPI, MCP, Codex, SQLite**  
Built an agentic operations system where OpenAI Codex uses custom MCP tools backed by REST APIs to search industrial products, retrieve inventory, access quotes and support tickets, and execute controlled business workflows. Implemented human-in-the-loop write approvals using short-lived single-use confirmation tokens, API validation, audit logging, webhook delivery, and MCP tool annotations; validated the system with **23 automated tests, 86% application coverage, and 15/15 agent evaluation scenarios passing**.

**Optional second bullet**  
Designed FastAPI/SQLite services for product search, inventory lookup, draft quotations, and technical-support workflows with structured JSON responses, business-rule validation, webhook failure isolation, and automated pytest regression testing.

## LinkedIn project description

Built an end-to-end AI operations agent using Python, FastAPI, SQLite, Model Context Protocol (MCP), and OpenAI Codex. The agent can search products, check live inventory, retrieve quotes/support tickets, and complete guarded business write workflows. Quote and support-ticket creation use a prepare/confirm/execute pattern with short-lived single-use tokens, while the backend records activity events and webhook delivery outcomes. The project includes 23 automated tests, 86% application coverage, 8/8 automated read evaluations, and 7/7 manual guarded-write evaluations.

## 60–90 second interview explanation

I wanted hands-on experience with MCP and agentic automation rather than building another prompt-only chatbot. I built a FastAPI backend with SQLite for products, inventory, customers, quotes, support tickets, and activity events, then exposed the business capabilities through a custom MCP server. Codex can automatically choose read-only tools for product and inventory questions. For write actions such as creating a quote or support ticket, I built a two-step workflow: the agent first prepares and validates the action, presents a summary, and only after explicit confirmation can a short-lived single-use token authorize the final write. The API also logs activity and sends webhook events. I validated the system with 23 regression tests, 86% coverage, eight automated agent read evaluations, and seven manual write-guardrail scenarios, all passing.

## Technical interview talking points

- Why MCP instead of direct LLM-to-database access: keeps the model behind explicit, typed business tools and preserves the API as the business-rule boundary.
- Why two write tools: makes intent and impact reviewable before state changes.
- Why short-lived single-use tokens: reduces replay and cross-action misuse.
- Why background webhooks: external delivery failure should not break the primary business transaction.
- Why automated + manual evals: deterministic read behavior can be automated; human-confirmation workflows need explicit human-in-the-loop verification.
