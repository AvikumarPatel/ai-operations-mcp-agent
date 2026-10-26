import logging
import os
import secrets
import time

from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

# ---------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = MCPServer(
    "AI Operations & Inventory",
    log_level="INFO",
)


# ---------------------------------------------------------
# REST API helper
# ---------------------------------------------------------

async def api_get(
    path: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """
    Send a GET request to the local business API and
    convert expected API errors into MCP ToolError messages.
    """

    url = f"{API_BASE_URL}{path}"

    try:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            response = await client.get(
                url,
                params=params,
            )

    except httpx.RequestError as exc:

        logger.error(
            "Unable to reach business API: %s",
            exc,
        )

        raise ToolError(
            "The business API is currently unavailable."
        ) from exc

    # -----------------------------------------------------
    # Friendly not-found handling
    # -----------------------------------------------------

    if response.status_code == 404:

        try:
            detail = response.json().get(
                "detail",
                "Resource not found.",
            )

        except ValueError:
            detail = "Resource not found."

        raise ToolError(detail)

    # -----------------------------------------------------
    # Other HTTP failures
    # -----------------------------------------------------

    if response.status_code >= 400:

        logger.error(
            "Business API returned status %s for %s",
            response.status_code,
            url,
        )

        raise ToolError(
            "The business API returned an error "
            f"(HTTP {response.status_code})."
        )

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:
        return response.json()

    except ValueError as exc:

        raise ToolError(
            "The business API returned invalid JSON."
        ) from exc

async def api_post(
    path: str,
    payload: dict[str, Any],
) -> Any:
    """
    Send a POST request to the local business API.

    Converts expected REST API failures into controlled
    MCP ToolError responses.
    """

    url = f"{API_BASE_URL}{path}"

    try:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            response = await client.post(
                url,
                json=payload,
            )

    except httpx.RequestError as exc:

        logger.error(
            "Unable to reach business API: %s",
            exc,
        )

        raise ToolError(
            "The business API is currently unavailable."
        ) from exc

    # -----------------------------------------------------
    # Common business errors
    # -----------------------------------------------------

    if response.status_code in {
        404,
        409,
        422,
    }:

        try:

            body = response.json()

            detail = body.get(
                "detail",
                "Business request failed.",
            )

        except ValueError:

            detail = "Business request failed."

        raise ToolError(
            str(detail)
        )

    # -----------------------------------------------------
    # Other HTTP errors
    # -----------------------------------------------------

    if response.status_code >= 400:

        raise ToolError(
            "The business API returned an error "
            f"(HTTP {response.status_code})."
        )

    try:

        return response.json()

    except ValueError as exc:

        raise ToolError(
            "The business API returned invalid JSON."
        ) from exc
CONFIRMATION_TTL_SECONDS = 300

pending_confirmations: dict[
    str,
    dict[str, Any],
] = {}

def create_confirmation(
    action: str,
    payload: dict[str, Any],
) -> str:
    """
    Create a single-use confirmation token for a pending
    write action.
    """

    token = secrets.token_urlsafe(24)

    pending_confirmations[token] = {
        "action": action,
        "payload": payload,
        "created_at": time.time(),
    }

    return token

def consume_confirmation(
    token: str,
    expected_action: str,
) -> dict[str, Any]:
    """
    Validate and consume a confirmation token.

    Tokens are:
    - single use
    - action specific
    - time limited
    """

    confirmation = pending_confirmations.pop(
        token,
        None,
    )

    if confirmation is None:

        raise ToolError(
            "Invalid or already-used confirmation token."
        )

    # -----------------------------------------------------
    # Check expiration
    # -----------------------------------------------------

    age = (
        time.time()
        - confirmation["created_at"]
    )

    if age > CONFIRMATION_TTL_SECONDS:

        raise ToolError(
            "Confirmation token has expired."
        )

    # -----------------------------------------------------
    # Check action
    # -----------------------------------------------------

    if (
        confirmation["action"]
        != expected_action
    ):

        raise ToolError(
            "Confirmation token is not valid "
            "for this action."
        )

    return confirmation["payload"]


# =========================================================
# MCP TOOLS
# =========================================================


@mcp.tool(
        title="Search Products",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    ),
)
async def search_products(
    category: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the industrial product catalog.

    Optionally filter products by category and/or maximum
    unit price. This is a read-only operation.
    """

    params: dict[str, Any] = {}

    if category:
        params["category"] = category

    if max_price is not None:

        if max_price < 0:
            raise ToolError(
                "max_price cannot be negative."
            )

        params["max_price"] = max_price

    products = await api_get(
        "/products",
        params=params,
    )

    return products


@mcp.tool(
        title="Get Product Details",
            annotations=ToolAnnotations(
                read_only_hint=True,
                open_world_hint=False,
        ),
)
async def get_product_details(
    sku: str,
) -> dict:
    """
    Retrieve detailed product information for a specific SKU.

    This tool is read-only and does not modify product data.
    """

    normalized_sku = sku.strip().upper()

    if not normalized_sku:
        raise ToolError(
            "SKU cannot be empty."
        )

    return await api_get(
        f"/products/{normalized_sku}"
    )


@mcp.tool(
        title="Check Inventory",
            annotations=ToolAnnotations(
                read_only_hint=True,
                open_world_hint=False,
        ),
)
async def check_inventory(
    sku: str,
) -> dict:
    """
    Check current inventory availability for a product SKU.

    Returns warehouse, available quantity, and reorder level.
    This tool is read-only.
    """

    normalized_sku = sku.strip().upper()

    if not normalized_sku:
        raise ToolError(
            "SKU cannot be empty."
        )

    return await api_get(
        f"/inventory/{normalized_sku}"
    )


@mcp.tool(
        title="Get Quote",
            annotations=ToolAnnotations(
                read_only_hint=True,
                open_world_hint=False,
        ),
)
async def get_quote(
    quote_id: str,
) -> dict:
    """
    Retrieve an existing quote by quote ID.

    This is a read-only operation and cannot create or
    modify a quote.
    """

    normalized_quote_id = (
        quote_id
        .strip()
        .upper()
    )

    if not normalized_quote_id:
        raise ToolError(
            "Quote ID cannot be empty."
        )

    return await api_get(
        f"/quotes/{normalized_quote_id}"
    )


@mcp.tool(
        title="Get Support Ticket",
            annotations=ToolAnnotations(
                read_only_hint=True,
                open_world_hint=False,
        ),
)
async def get_support_ticket(
    ticket_id: str,
) -> dict:
    """
    Retrieve an existing support ticket by ticket ID.

    This is a read-only operation and cannot create or
    modify a support ticket.
    """

    normalized_ticket_id = (
        ticket_id
        .strip()
        .upper()
    )

    if not normalized_ticket_id:
        raise ToolError(
            "Ticket ID cannot be empty."
        )

    return await api_get(
        f"/support-tickets/{normalized_ticket_id}"
    )

@mcp.tool(
    title="Prepare Quote Draft",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    ),
)
async def prepare_quote_draft(
    customer_code: str,
    sku: str,
    quantity: int,
) -> dict:
    """
    Prepare a draft quote request for human confirmation.

    This tool does not create the quote.
    It validates product/inventory information and returns
    a short-lived confirmation token.
    """

    normalized_customer = (
        customer_code
        .strip()
        .upper()
    )

    normalized_sku = (
        sku
        .strip()
        .upper()
    )

    if not normalized_customer:

        raise ToolError(
            "Customer code cannot be empty."
        )

    if not normalized_sku:

        raise ToolError(
            "SKU cannot be empty."
        )

    if quantity <= 0:

        raise ToolError(
            "Quantity must be greater than zero."
        )

    # -----------------------------------------------------
    # Validate product
    # -----------------------------------------------------

    product = await api_get(
        f"/products/{normalized_sku}"
    )

    # -----------------------------------------------------
    # Validate inventory
    # -----------------------------------------------------

    inventory = await api_get(
        f"/inventory/{normalized_sku}"
    )

    available = inventory[
        "quantity_available"
    ]

    if quantity > available:

        raise ToolError(
            f"Requested quantity ({quantity}) exceeds "
            f"available inventory ({available})."
        )

    unit_price = float(
        product["unit_price"]
    )

    subtotal = round(
        unit_price * quantity,
        2,
    )

    payload = {
        "customer_code": normalized_customer,
        "sku": normalized_sku,
        "quantity": quantity,
    }

    confirmation_token = (
        create_confirmation(
            action="create_quote_draft",
            payload=payload,
        )
    )

    return {
        "confirmation_required": True,
        "action": "create_quote_draft",
        "confirmation_token": (
            confirmation_token
        ),
        "expires_in_seconds": (
            CONFIRMATION_TTL_SECONDS
        ),
        "summary": {
            "customer_code": (
                normalized_customer
            ),
            "sku": normalized_sku,
            "product_name": product[
                "product_name"
            ],
            "quantity": quantity,
            "available_inventory": available,
            "unit_price": unit_price,
            "estimated_subtotal": subtotal,
            "status": "draft",
        },
        "instruction": (
            "Present this summary to the user. "
            "Do not call create_quote_draft until "
            "the user explicitly confirms."
        ),
    }

@mcp.tool(
    title="Create Quote Draft",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
)
async def create_quote_draft(
    confirmation_token: str,
) -> dict:
    """
    Create a draft quote only after confirmation.

    Requires a valid single-use confirmation token generated
    by prepare_quote_draft.
    """

    payload = consume_confirmation(
        token=confirmation_token,
        expected_action="create_quote_draft",
    )

    result = await api_post(
        "/quotes",
        payload,
    )

    return {
        "success": True,
        "message": (
            "Draft quote created successfully."
        ),
        "quote": result,
    }

@mcp.tool(
    title="Prepare Support Ticket",
    annotations=ToolAnnotations(
        read_only_hint=True,
        open_world_hint=False,
    ),
)
async def prepare_support_ticket(
    customer_code: str,
    issue: str,
    severity: str,
    sku: str | None = None,
) -> dict:
    """
    Prepare a support ticket for human confirmation.

    This tool does not create the ticket.
    """

    normalized_customer = (
        customer_code
        .strip()
        .upper()
    )

    normalized_issue = issue.strip()

    normalized_severity = (
        severity
        .strip()
        .lower()
    )

    allowed_severities = {
        "low",
        "medium",
        "high",
        "critical",
    }

    if not normalized_customer:

        raise ToolError(
            "Customer code cannot be empty."
        )

    if len(normalized_issue) < 10:

        raise ToolError(
            "Issue description must contain "
            "at least 10 characters."
        )

    if (
        normalized_severity
        not in allowed_severities
    ):

        raise ToolError(
            "Severity must be one of: "
            "low, medium, high, critical."
        )

    normalized_sku = None
    product_name = None

    if sku:

        normalized_sku = (
            sku
            .strip()
            .upper()
        )

        product = await api_get(
            f"/products/{normalized_sku}"
        )

        product_name = product[
            "product_name"
        ]

    payload = {
        "customer_code": (
            normalized_customer
        ),
        "sku": normalized_sku,
        "issue": normalized_issue,
        "severity": normalized_severity,
    }

    confirmation_token = (
        create_confirmation(
            action="create_support_ticket",
            payload=payload,
        )
    )

    return {
        "confirmation_required": True,
        "action": "create_support_ticket",
        "confirmation_token": (
            confirmation_token
        ),
        "expires_in_seconds": (
            CONFIRMATION_TTL_SECONDS
        ),
        "summary": {
            "customer_code": (
                normalized_customer
            ),
            "sku": normalized_sku,
            "product_name": product_name,
            "issue": normalized_issue,
            "severity": normalized_severity,
            "status": "open",
        },
        "instruction": (
            "Present this summary to the user. "
            "Do not call create_support_ticket until "
            "the user explicitly confirms."
        ),
    }

@mcp.tool(
    title="Create Support Ticket",
    annotations=ToolAnnotations(
        read_only_hint=False,
        destructive_hint=False,
        idempotent_hint=False,
        open_world_hint=False,
    ),
)
async def create_support_ticket(
    confirmation_token: str,
) -> dict:
    """
    Create a support ticket only after confirmation.

    Requires a valid single-use token generated by
    prepare_support_ticket.
    """

    payload = consume_confirmation(
        token=confirmation_token,
        expected_action=(
            "create_support_ticket"
        ),
    )

    result = await api_post(
        "/support-tickets",
        payload,
    )

    return {
        "success": True,
        "message": (
            "Support ticket created successfully."
        ),
        "support_ticket": result,
    }

# ---------------------------------------------------------
# Run local MCP server
# ---------------------------------------------------------

if __name__ == "__main__":
    mcp.run()