# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Request validation helpers."""

from typing import Optional


def validate_reserve_request(data: dict) -> Optional[str]:
    """Validate a stock reservation request. Returns error string or None."""
    if not data.get("product_id"):
        return "product_id is required"

    quantity = data.get("quantity", 1)
    if not isinstance(quantity, int) or quantity < 1:
        return "quantity must be a positive integer"

    if quantity > 50:
        return "quantity exceeds maximum of 50 per reservation"

    return None


def validate_release_request(data: dict) -> Optional[str]:
    """Validate a stock release request. Returns error string or None."""
    if not data.get("product_id"):
        return "product_id is required"

    quantity = data.get("quantity", 1)
    if not isinstance(quantity, int) or quantity < 1:
        return "quantity must be a positive integer"

    return None
