# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Custom application metrics for the inventory service."""

from opentelemetry import metrics


class InventoryMetrics:
    """Container for all inventory-specific metrics instruments."""

    def __init__(self, meter: metrics.Meter):
        self.reservation_counter = meter.create_counter(
            name="inventory.reservations_total",
            description="Total number of inventory reservations",
            unit="reservations",
        )

        self.reservation_failure_counter = meter.create_counter(
            name="inventory.reservation_failures_total",
            description="Total failed reservation attempts",
            unit="failures",
        )

        self.low_stock_counter = meter.create_up_down_counter(
            name="inventory.low_stock_products",
            description="Number of products with stock below threshold",
            unit="products",
        )

        self.restock_counter = meter.create_counter(
            name="inventory.restocks_total",
            description="Total number of restock events",
            unit="restocks",
        )

        self.reservation_latency = meter.create_histogram(
            name="inventory.reservation_duration_seconds",
            description="Time taken to process a reservation",
            unit="s",
        )

    def record_reservation(self, product_id: str, quantity: int):
        self.reservation_counter.add(quantity, {"product.id": product_id})

    def record_reservation_failure(self, product_id: str, reason: str):
        self.reservation_failure_counter.add(
            1, {"product.id": product_id, "reason": reason}
        )

    def record_low_stock(self, product_id: str):
        self.low_stock_counter.add(1, {"product.id": product_id})

    def record_restock(self, product_id: str, quantity: int):
        self.restock_counter.add(quantity, {"product.id": product_id})
