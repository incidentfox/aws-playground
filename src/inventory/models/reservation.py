# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Reservation domain model."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReservationStatus(str, Enum):
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class Reservation:
    product_id: str
    quantity: int
    order_id: str = ""
    reservation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ReservationStatus = ReservationStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> dict:
        return {
            "reservation_id": self.reservation_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "order_id": self.order_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
