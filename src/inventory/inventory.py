#!/usr/bin/env python3
# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Inventory Service - Tracks product stock levels and availability."""

import logging
import os
import random
import threading
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

# --- Configuration ---
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "inventory")
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
PRODUCT_CATALOG_ADDR = os.getenv("PRODUCT_CATALOG_SERVICE_ADDR", "product-catalog:8080")
PORT = int(os.getenv("INVENTORY_SERVICE_PORT", "8080"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Logging ---
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(SERVICE_NAME)

# --- OpenTelemetry Setup ---
resource = Resource.create({
    ResourceAttributes.SERVICE_NAME: SERVICE_NAME,
    ResourceAttributes.SERVICE_VERSION: "0.1.0",
    "service.namespace": "opentelemetry-demo",
})

# Traces
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(SERVICE_NAME, "0.1.0")

# Metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True),
    export_interval_millis=60000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(SERVICE_NAME, "0.1.0")

# --- Custom Metrics ---
stock_level_gauge = meter.create_observable_gauge(
    name="inventory.stock_level",
    description="Current stock level per product",
    unit="items",
)

reservation_counter = meter.create_counter(
    name="inventory.reservations_total",
    description="Total number of inventory reservations",
    unit="reservations",
)

reservation_failure_counter = meter.create_counter(
    name="inventory.reservation_failures_total",
    description="Total number of failed reservation attempts (insufficient stock)",
    unit="failures",
)

low_stock_gauge = meter.create_up_down_counter(
    name="inventory.low_stock_products",
    description="Number of products with stock below threshold",
    unit="products",
)

# --- In-Memory Inventory Store ---
LOW_STOCK_THRESHOLD = 10

inventory_store = {
    "OLJCESPC7Z": {"name": "National Park Foundation Explorascope", "quantity": 100, "reserved": 0},
    "66VCHSJNUP": {"name": "Starsense Explorer Telescope", "quantity": 50, "reserved": 0},
    "1YMWWN1N4O": {"name": "Roof Binoculars", "quantity": 200, "reserved": 0},
    "L9ECAV7KIM": {"name": "Eclipsmart Travel Refractor Telescope", "quantity": 30, "reserved": 0},
    "2ZYFJ3GM2N": {"name": "Solar System Color Imager", "quantity": 75, "reserved": 0},
    "0PUK6V6EV0": {"name": "Solar Filter", "quantity": 150, "reserved": 0},
    "LS4PSXUNUM": {"name": "Red Flashlight", "quantity": 500, "reserved": 0},
    "9SIQT8TOJO": {"name": "Optical Tube Assembly", "quantity": 25, "reserved": 0},
    "6E92ZMYYFZ": {"name": "The Comet Book", "quantity": 300, "reserved": 0},
    "HQTGWGPNH4": {"name": "Lens Cleaning Kit", "quantity": 1000, "reserved": 0},
}

store_lock = threading.Lock()


def get_stock_observations(options):
    """Observable callback for stock level gauge."""
    measurements = []
    with store_lock:
        for product_id, item in inventory_store.items():
            available = item["quantity"] - item["reserved"]
            measurements.append(
                metrics.Observation(
                    value=available,
                    attributes={"product.id": product_id, "product.name": item["name"]},
                )
            )
    return measurements


stock_level_gauge = meter.create_observable_gauge(
    name="inventory.stock_level",
    description="Current stock level per product",
    unit="items",
    callbacks=[get_stock_observations],
)


# --- Flask App ---
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": SERVICE_NAME})


@app.route("/api/inventory", methods=["GET"])
def list_inventory():
    """List all products and their stock levels."""
    with tracer.start_as_current_span("list_inventory") as span:
        with store_lock:
            result = []
            for product_id, item in inventory_store.items():
                available = item["quantity"] - item["reserved"]
                result.append({
                    "product_id": product_id,
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "reserved": item["reserved"],
                    "available": available,
                    "low_stock": available < LOW_STOCK_THRESHOLD,
                })

        span.set_attribute("inventory.product_count", len(result))
        low_stock_count = sum(1 for p in result if p["low_stock"])
        span.set_attribute("inventory.low_stock_count", low_stock_count)

        logger.info("Listed inventory: %d products, %d low stock", len(result), low_stock_count)
        return jsonify({"products": result})


@app.route("/api/inventory/<product_id>", methods=["GET"])
def get_product_stock(product_id):
    """Get stock level for a specific product."""
    with tracer.start_as_current_span("get_product_stock") as span:
        span.set_attribute("product.id", product_id)

        with store_lock:
            item = inventory_store.get(product_id)
            if not item:
                span.set_attribute("error", True)
                logger.warning("Product not found: %s", product_id)
                return jsonify({"error": "Product not found", "product_id": product_id}), 404

            available = item["quantity"] - item["reserved"]

        span.set_attribute("inventory.available", available)
        span.set_attribute("product.name", item["name"])

        return jsonify({
            "product_id": product_id,
            "name": item["name"],
            "quantity": item["quantity"],
            "reserved": item["reserved"],
            "available": available,
            "low_stock": available < LOW_STOCK_THRESHOLD,
        })


@app.route("/api/inventory/reserve", methods=["POST"])
def reserve_stock():
    """Reserve stock for a product (called during checkout)."""
    with tracer.start_as_current_span("reserve_stock") as span:
        data = request.get_json() or {}
        product_id = data.get("product_id", "")
        quantity = data.get("quantity", 1)

        span.set_attribute("product.id", product_id)
        span.set_attribute("reservation.quantity", quantity)

        with store_lock:
            item = inventory_store.get(product_id)
            if not item:
                span.set_attribute("error", True)
                reservation_failure_counter.add(1, {"product.id": product_id, "reason": "not_found"})
                logger.error("Reservation failed - product not found: %s", product_id)
                return jsonify({"error": "Product not found"}), 404

            available = item["quantity"] - item["reserved"]
            if available < quantity:
                span.set_attribute("error", True)
                span.set_attribute("inventory.available", available)
                reservation_failure_counter.add(1, {"product.id": product_id, "reason": "insufficient_stock"})
                logger.warning(
                    "Reservation failed - insufficient stock for %s: requested=%d, available=%d",
                    product_id, quantity, available,
                )
                return jsonify({
                    "error": "Insufficient stock",
                    "available": available,
                    "requested": quantity,
                }), 409

            item["reserved"] += quantity
            new_available = item["quantity"] - item["reserved"]

        reservation_counter.add(quantity, {"product.id": product_id})

        if new_available < LOW_STOCK_THRESHOLD:
            low_stock_gauge.add(1, {"product.id": product_id})
            logger.warning("Low stock alert: %s (%s) has %d remaining", product_id, item["name"], new_available)

        span.set_attribute("inventory.available_after", new_available)
        logger.info("Reserved %d of %s (%s), %d remaining", quantity, product_id, item["name"], new_available)

        return jsonify({
            "product_id": product_id,
            "reserved": quantity,
            "available_after": new_available,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


@app.route("/api/inventory/release", methods=["POST"])
def release_stock():
    """Release previously reserved stock (e.g. cancelled order)."""
    with tracer.start_as_current_span("release_stock") as span:
        data = request.get_json() or {}
        product_id = data.get("product_id", "")
        quantity = data.get("quantity", 1)

        span.set_attribute("product.id", product_id)
        span.set_attribute("release.quantity", quantity)

        with store_lock:
            item = inventory_store.get(product_id)
            if not item:
                return jsonify({"error": "Product not found"}), 404

            item["reserved"] = max(0, item["reserved"] - quantity)
            new_available = item["quantity"] - item["reserved"]

        span.set_attribute("inventory.available_after", new_available)
        logger.info("Released %d of %s (%s), %d now available", quantity, product_id, item["name"], new_available)

        return jsonify({
            "product_id": product_id,
            "released": quantity,
            "available_after": new_available,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


if __name__ == "__main__":
    logger.info("Inventory service starting on port %d", PORT)
    app.run(host="0.0.0.0", port=PORT)
