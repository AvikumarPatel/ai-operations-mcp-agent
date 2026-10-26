from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    sku: str
    product_name: str
    category: str
    manufacturer: str
    description: str
    unit_price: float

    model_config = {"from_attributes": True}


class InventoryResponse(BaseModel):
    sku: str
    warehouse: str
    quantity_available: int
    reorder_level: int

    model_config = {"from_attributes": True}


# -------------------------
# QUOTES
# -------------------------

class QuoteCreate(BaseModel):
    customer_code: str
    sku: str

    quantity: int = Field(
        gt=0,
        le=10000,
    )


class QuoteResponse(BaseModel):
    quote_id: str
    customer_code: str
    sku: str
    quantity: int
    unit_price: float
    subtotal: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# -------------------------
# SUPPORT TICKETS
# -------------------------

class SupportTicketCreate(BaseModel):
    customer_code: str
    sku: str | None = None

    issue: str = Field(
        min_length=10,
        max_length=2000,
    )

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]


class SupportTicketResponse(BaseModel):
    ticket_id: str
    customer_code: str
    sku: str | None
    issue: str
    severity: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# -------------------------
# ACTIVITY LOG
# -------------------------

class ActivityResponse(BaseModel):
    id: int
    event_type: str
    entity_type: str
    entity_id: str
    details: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class WebhookEvent(BaseModel):
    event_type: str
    entity_type: str
    entity_id: str
    payload: dict = Field(
        default_factory=dict
    )