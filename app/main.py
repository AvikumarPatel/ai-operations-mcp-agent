import json
import os
import httpx

from dotenv import load_dotenv
from datetime import datetime

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, SessionLocal

from app.models import (
    ActivityLog,
    Customer,
    Inventory,
    Product,
    Quote,
    SupportTicket,
)

from app.schemas import (
    ActivityResponse,
    InventoryResponse,
    ProductResponse,
    QuoteCreate,
    QuoteResponse,
    SupportTicketCreate,
    SupportTicketResponse,
    WebhookEvent,
)

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Operations API",
    description=(
        "REST API for products, inventory, quotes, "
        "support tickets, and AI automation tools."
    ),
    version="1.0.0",
)

def log_activity(
    db: Session,
    event_type: str,
    entity_type: str,
    entity_id: str,
    details: dict | None = None,
):
    activity = ActivityLog(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=(
            json.dumps(details)
            if details is not None
            else None
        ),
    )

    db.add(activity)
async def send_webhook_event(
    event: dict,
):
    """
    Send an outbound business event to the configured
    webhook URL without blocking the main API request.
    """

    webhook_url = os.getenv(
        "WEBHOOK_URL",
        ""
    ).strip()

    # Webhooks can be disabled simply by leaving
    # WEBHOOK_URL blank.
    if not webhook_url:
        return

    db = SessionLocal()

    try:

        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:

            response = await client.post(
                webhook_url,
                json=event,
            )

            response.raise_for_status()

        log_activity(
            db=db,
            event_type="WEBHOOK_DELIVERED",
            entity_type=event["entity_type"],
            entity_id=event["entity_id"],
            details={
                "source_event": event[
                    "event_type"
                ],
                "target_url": webhook_url,
                "status_code": (
                    response.status_code
                ),
            },
        )

        db.commit()

    except Exception as exc:

        db.rollback()

        log_activity(
            db=db,
            event_type="WEBHOOK_FAILED",
            entity_type=event.get(
                "entity_type",
                "unknown",
            ),
            entity_id=event.get(
                "entity_id",
                "unknown",
            ),
            details={
                "source_event": event.get(
                    "event_type"
                ),
                "target_url": webhook_url,
                "error": str(exc),
            },
        )

        db.commit()

    finally:

        db.close()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Operations API",
    }


@app.get(
    "/products",
    response_model=list[ProductResponse],
)
def list_products(
    category: str | None = Query(default=None),
    max_price: float | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    query = db.query(Product)

    if category:
        query = query.filter(
            Product.category.ilike(f"%{category}%")
        )

    if max_price:
        query = query.filter(
            Product.unit_price <= max_price
        )

    return query.all()


@app.get(
    "/products/{sku}",
    response_model=ProductResponse,
)
def get_product(
    sku: str,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.sku == sku.upper())
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@app.get(
    "/inventory/{sku}",
    response_model=InventoryResponse,
)
def get_inventory(
    sku: str,
    db: Session = Depends(get_db),
):
    inventory = (
        db.query(Inventory)
        .filter(Inventory.sku == sku.upper())
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found",
        )

    return inventory

@app.post(
    "/quotes",
    response_model=QuoteResponse,
    status_code=201,
)
def create_quote(
    quote_request: QuoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    customer_code = quote_request.customer_code.upper()
    sku = quote_request.sku.upper()

    # -------------------------
    # Validate customer
    # -------------------------

    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_code == customer_code
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    # -------------------------
    # Validate product
    # -------------------------

    product = (
        db.query(Product)
        .filter(Product.sku == sku)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # -------------------------
    # Validate inventory
    # -------------------------

    inventory = (
        db.query(Inventory)
        .filter(Inventory.sku == sku)
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found",
        )

    if inventory.quantity_available < quote_request.quantity:
        raise HTTPException(
            status_code=409,
            detail=(
                "Requested quantity exceeds "
                "available inventory"
            ),
        )

    # -------------------------
    # Generate quote ID
    # -------------------------

    latest_quote = (
        db.query(Quote)
        .order_by(Quote.id.desc())
        .first()
    )

    next_number = (
        latest_quote.id + 1
        if latest_quote
        else 1
    )

    quote_id = f"Q-{next_number:04d}"

    subtotal = (
        product.unit_price
        * quote_request.quantity
    )

    quote = Quote(
        quote_id=quote_id,
        customer_code=customer_code,
        sku=sku,
        quantity=quote_request.quantity,
        unit_price=product.unit_price,
        subtotal=round(subtotal, 2),
        status="draft",
    )

    db.add(quote)

    log_activity(
        db=db,
        event_type="QUOTE_CREATED",
        entity_type="quote",
        entity_id=quote_id,
        details={
            "customer_code": customer_code,
            "sku": sku,
            "quantity": quote_request.quantity,
            "status": "draft",
        },
    )

    db.commit()
    db.refresh(quote)

    background_tasks.add_task(
    send_webhook_event,
    {
        "event_type": "QUOTE_CREATED",
        "entity_type": "quote",
        "entity_id": quote.quote_id,
        "payload": {
            "customer_code": (
                quote.customer_code
            ),
            "sku": quote.sku,
            "quantity": quote.quantity,
            "subtotal": float(quote.subtotal),
            "status": quote.status,
        },
    },
)

    return quote

@app.get(
    "/quotes/{quote_id}",
    response_model=QuoteResponse,
)
def get_quote(
    quote_id: str,
    db: Session = Depends(get_db),
):

    quote = (
        db.query(Quote)
        .filter(
            Quote.quote_id
            == quote_id.upper()
        )
        .first()
    )

    if not quote:
        raise HTTPException(
            status_code=404,
            detail="Quote not found",
        )

    return quote

@app.post(
    "/support-tickets",
    response_model=SupportTicketResponse,
    status_code=201,
)
def create_support_ticket(
    ticket_request: SupportTicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):

    customer_code = (
        ticket_request
        .customer_code
        .upper()
    )

    # -------------------------
    # Validate customer
    # -------------------------

    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_code
            == customer_code
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    # -------------------------
    # Validate SKU if provided
    # -------------------------

    sku = None

    if ticket_request.sku:

        sku = ticket_request.sku.upper()

        product = (
            db.query(Product)
            .filter(Product.sku == sku)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

    # -------------------------
    # Generate ticket ID
    # -------------------------

    latest_ticket = (
        db.query(SupportTicket)
        .order_by(
            SupportTicket.id.desc()
        )
        .first()
    )

    next_number = (
        latest_ticket.id + 1
        if latest_ticket
        else 1
    )

    ticket_id = f"T-{next_number:04d}"

    ticket = SupportTicket(
        ticket_id=ticket_id,
        customer_code=customer_code,
        sku=sku,
        issue=ticket_request.issue,
        severity=ticket_request.severity,
        status="open",
    )

    db.add(ticket)

    log_activity(
        db=db,
        event_type="SUPPORT_TICKET_CREATED",
        entity_type="support_ticket",
        entity_id=ticket_id,
        details={
            "customer_code": customer_code,
            "sku": sku,
            "severity": ticket_request.severity,
        },
    )

    db.commit()
    db.refresh(ticket)

    background_tasks.add_task(
    send_webhook_event,
    {
        "event_type": (
            "SUPPORT_TICKET_CREATED"
        ),
        "entity_type": (
            "support_ticket"
        ),
        "entity_id": (
            ticket.ticket_id
        ),
        "payload": {
            "customer_code": (
                ticket.customer_code
            ),
            "sku": ticket.sku,
            "severity": (
                ticket.severity
            ),
            "status": ticket.status,
        },
    },
)

    return ticket

@app.get(
    "/support-tickets/{ticket_id}",
    response_model=SupportTicketResponse,
)
def get_support_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
):

    ticket = (
        db.query(SupportTicket)
        .filter(
            SupportTicket.ticket_id
            == ticket_id.upper()
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    return ticket

@app.get(
    "/activity",
    response_model=list[ActivityResponse],
)
def list_activity(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):

    return (
        db.query(ActivityLog)
        .order_by(
            ActivityLog.id.desc()
        )
        .limit(limit)
        .all()
    )

@app.post(
    "/webhooks/activity",
    status_code=202,
)
def receive_activity_webhook(
    event: WebhookEvent,
    db: Session = Depends(get_db),
):

    log_activity(
        db=db,
        event_type="WEBHOOK_RECEIVED",
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        details={
            "source_event": (
                event.event_type
            ),
            "payload": event.payload,
        },
    )

    db.commit()

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "entity_id": event.entity_id,
    }