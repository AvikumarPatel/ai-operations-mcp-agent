# Testing and Evaluation

## Backend regression suite

The project currently passes **23/23** pytest tests with **86%** application coverage.

Covered behaviors include:

- health endpoint
- product listing and filters
- product lookup
- inventory lookup
- 404 handling
- quote creation/retrieval
- invalid customers/products
- insufficient inventory
- quantity validation
- support-ticket creation/retrieval
- severity validation
- webhook receiver
- activity logging
- MCP tool registration

## Automated agent evaluations

`evals/read_only_cases.json` defines eight read-only cases. `evals/run_read_only_evals.py` runs Codex in structured JSON mode and verifies expected MCP tool usage.

Validated cases:

1. product search
2. product details
3. inventory lookup
4. product + inventory multi-tool request
5. multi-tool search + fulfillment check
6. invalid SKU / no hallucination
7. quote lookup
8. support-ticket lookup

Result: **8/8 passed**.

## Manual guarded-write evaluations

`evals/manual_write_evals.md` records seven human-in-the-loop scenarios:

1. quote preparation
2. confirmed quote creation
3. quote cancellation
4. support-ticket preparation
5. confirmed support-ticket creation
6. invalid SKU rejection
7. excess-inventory rejection

Result: **7/7 passed**.

Combined agent evaluation result: **15/15 scenarios passed**.

## Reproduce

```bash
python -m pytest -v
python -m pytest --cov=app --cov-report=term
python evals/run_read_only_evals.py
```

Write evaluations are intentionally manual because they test explicit human confirmation behavior.
