# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""HTTP route definitions for the inventory service."""

import time
from datetime import datetime, timezone

from flask import Blueprint, Flask, jsonify, request
from opentelemetry import trace

from api.validators import validate_reserve_request, validate_release_request

inventory_bp = Blueprint("inventory", __name__)
tracer = trace.get_tracer(__name__)

# These are injected at registration time.
_store = None
_metrics = None


def register_routes(app: Flask, store, metrics_instance):
    global _store, _metrics
    _store = store
    _metrics = metrics_instance
    app.register_blueprint(inventory_bp)


@inventory_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "inventory", "timestamp": datetime.now(timezone.utc).isoformat()})


@inventory_bp.route("/api/inventory", methods=["GET"])
def list_inventory():
    with tracer.start_as_current_span("list_inventory") as span:
        products = _store.list_products()
        result = [p.to_dict() for p in products]
        low = sum(1 for p in products if p.status.value == "low_stock")
        oos = sum(1 for p in products if p.status.value == "out_of_stock")

        span.set_attribute("inventory.product_count", len(result))
        span.set_attribute("inventory.low_stock_count", low)
        span.set_attribute("inventory.out_of_stock_count", oos)

        return jsonify({"products": result, "total": len(result), "low_stock": low, "out_of_stock": oos})


@inventory_bp.route("/api/inventory/<product_id>", methods=["GET"])
def get_product_stock(product_id):
    with tracer.start_as_current_span("get_product_stock") as span:
        span.set_attribute("product.id", product_id)
        product = _store.get_product(product_id)
        if product is None:
            span.set_status(trace.StatusCode.ERROR, "Product not found")
            return jsonify({"error": "Product not found", "product_id": product_id}), 404
        span.set_attribute("product.name", product.name)
        span.set_attribute("inventory.available", product.available)
        return jsonify(product.to_dict())


@inventory_bp.route("/api/inventory/reserve", methods=["POST"])
def reserve_stock():
    with tracer.start_as_current_span("reserve_stock") as span:
        data = request.get_json(silent=True) or {}
        error = validate_reserve_request(data)
        if error:
            span.set_status(trace.StatusCode.ERROR, error)
            return jsonify({"error": error}), 400

        product_id = data["product_id"]
        quantity = data.get("quantity", 1)
        order_id = data.get("order_id", "")

        span.set_attribute("product.id", product_id)
        span.set_attribute("reservation.quantity", quantity)
        span.set_attribute("order.id", order_id)

        start = time.monotonic()
        reservation = _store.reserve(product_id, quantity, order_id)
        elapsed = time.monotonic() - start

        _metrics.reservation_latency.record(elapsed, {"product.id": product_id})

        if reservation is None:
            product = _store.get_product(product_id)
            if product is None:
                _metrics.record_reservation_failure(product_id, "not_found")
                span.set_status(trace.StatusCode.ERROR, "Product not found")
                return jsonify({"error": "Product not found"}), 404
            else:
                _metrics.record_reservation_failure(product_id, "insufficient_stock")
                span.set_status(trace.StatusCode.ERROR, "Insufficient stock")
                return jsonify({
                    "error": "Insufficient stock",
                    "available": product.available,
                    "requested": quantity,
                }), 409

        _metrics.record_reservation(product_id, quantity)

        product = _store.get_product(product_id)
        if product and product.status.value == "low_stock":
            _metrics.record_low_stock(product_id)

        span.set_attribute("reservation.id", reservation.reservation_id)
        return jsonify(reservation.to_dict()), 201


@inventory_bp.route("/api/inventory/release", methods=["POST"])
def release_stock():
    with tracer.start_as_current_span("release_stock") as span:
        data = request.get_json(silent=True) or {}
        error = validate_release_request(data)
        if error:
            span.set_status(trace.StatusCode.ERROR, error)
            return jsonify({"error": error}), 400

        product_id = data["product_id"]
        quantity = data.get("quantity", 1)

        span.set_attribute("product.id", product_id)
        span.set_attribute("release.quantity", quantity)

        success = _store.release(product_id, quantity)
        if not success:
            span.set_status(trace.StatusCode.ERROR, "Product not found")
            return jsonify({"error": "Product not found"}), 404

        product = _store.get_product(product_id)
        return jsonify({
            "product_id": product_id,
            "released": quantity,
            "available_after": product.available if product else 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
