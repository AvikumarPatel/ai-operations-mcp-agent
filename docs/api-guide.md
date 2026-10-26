# API Guide

## Product search

`GET /products`

Optional query parameters:

- `category`
- `max_price`

Example:

```text
GET /products?category=Sensors&max_price=50
```

## Product details

```text
GET /products/PRX-001
```

Unknown products return `404 Product not found`.

## Inventory

```text
GET /inventory/PRX-001
```

Unknown inventory records return `404 Inventory record not found`.

## Create a draft quote

`POST /quotes`

```json
{
  "customer_code": "CUST-001",
  "sku": "PRX-001",
  "quantity": 20
}
```

The service validates customer, product, quantity, and available inventory. Insufficient inventory returns a conflict response rather than creating the quote.

## Create a support ticket

`POST /support-tickets`

```json
{
  "customer_code": "CUST-002",
  "sku": "TMP-210",
  "issue": "Temperature readings fluctuate during normal production.",
  "severity": "high"
}
```

Supported severities are `low`, `medium`, `high`, and `critical`.

## Activity log

`GET /activity`

Used to verify business events such as:

- `QUOTE_CREATED`
- `SUPPORT_TICKET_CREATED`
- `WEBHOOK_RECEIVED`
- `WEBHOOK_DELIVERED`
- `WEBHOOK_FAILED`

## Webhook receiver

`POST /webhooks/activity`

The local project uses this endpoint as a demonstration receiver. The configured `WEBHOOK_URL` can later point to another automation platform or service.
