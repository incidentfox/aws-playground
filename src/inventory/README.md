# Inventory Service

The inventory service tracks product stock levels and availability for the
Astronomy Shop. It is called by the checkout service to reserve stock when
a customer places an order.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/api/inventory` | GET | List all products and stock levels |
| `/api/inventory/{product_id}` | GET | Get stock for a specific product |
| `/api/inventory/reserve` | POST | Reserve stock (called during checkout) |
| `/api/inventory/release` | POST | Release reserved stock (cancelled order) |

## Telemetry

This service emits the following custom metrics:

| Metric | Type | Description |
|---|---|---|
| `inventory.stock_level` | Gauge | Current available stock per product |
| `inventory.reservations_total` | Counter | Total reservations made |
| `inventory.reservation_failures_total` | Counter | Failed reservations (insufficient stock) |
| `inventory.low_stock_products` | UpDownCounter | Products below low-stock threshold |

Traces are emitted for all API operations with attributes including
`product.id`, `product.name`, `inventory.available`, and reservation details.
