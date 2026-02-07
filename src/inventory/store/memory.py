# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Thread-safe in-memory inventory store with reservation tracking."""

import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from models.product import Product, StockStatus
from models.reservation import Reservation, ReservationStatus

logger = logging.getLogger(__name__)


class InMemoryInventoryStore:
    """In-memory store for product stock and reservations.

    In a production system this would be backed by PostgreSQL or similar,
    but for the demo an in-memory store keeps the service self-contained.
    """

    def __init__(self, reservation_ttl_seconds: int = 900):
        self._products: Dict[str, Product] = {}
        self._reservations: Dict[str, Reservation] = {}
        self._lock = threading.Lock()
        self._reservation_ttl = reservation_ttl_seconds
        self._seed_catalog()

    def _seed_catalog(self):
        """Pre-populate with the Astronomy Shop product catalog."""
        catalog = [
            ("OLJCESPC7Z", "National Park Foundation Explorascope", 100),
            ("66VCHSJNUP", "Starsense Explorer Telescope", 50),
            ("1YMWWN1N4O", "Roof Binoculars", 200),
            ("L9ECAV7KIM", "Eclipsmart Travel Refractor Telescope", 30),
            ("2ZYFJ3GM2N", "Solar System Color Imager", 75),
            ("0PUK6V6EV0", "Solar Filter", 150),
            ("LS4PSXUNUM", "Red Flashlight", 500),
            ("9SIQT8TOJO", "Optical Tube Assembly", 25),
            ("6E92ZMYYFZ", "The Comet Book", 300),
            ("HQTGWGPNH4", "Lens Cleaning Kit", 1000),
        ]
        for pid, name, qty in catalog:
            self._products[pid] = Product(product_id=pid, name=name, quantity=qty)

    def list_products(self) -> List[Product]:
        with self._lock:
            return list(self._products.values())

    def get_product(self, product_id: str) -> Optional[Product]:
        with self._lock:
            return self._products.get(product_id)

    def reserve(self, product_id: str, quantity: int,
                order_id: str = "") -> Optional[Reservation]:
        """Attempt to reserve stock. Returns Reservation on success, None on failure."""
        with self._lock:
            product = self._products.get(product_id)
            if product is None:
                return None

            if product.available < quantity:
                return None

            product.reserved += quantity

            reservation = Reservation(
                product_id=product_id,
                quantity=quantity,
                order_id=order_id,
                expires_at=datetime.now(timezone.utc) + timedelta(
                    seconds=self._reservation_ttl
                ),
            )
            self._reservations[reservation.reservation_id] = reservation
            return reservation

    def release(self, product_id: str, quantity: int) -> bool:
        with self._lock:
            product = self._products.get(product_id)
            if product is None:
                return False
            product.reserved = max(0, product.reserved - quantity)
            return True

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        with self._lock:
            return self._reservations.get(reservation_id)

    def expire_reservations(self) -> int:
        """Expire stale reservations and release stock. Returns count expired."""
        expired_count = 0
        with self._lock:
            for res in list(self._reservations.values()):
                if res.status == ReservationStatus.ACTIVE and res.is_expired():
                    res.status = ReservationStatus.EXPIRED
                    product = self._products.get(res.product_id)
                    if product:
                        product.reserved = max(0, product.reserved - res.quantity)
                    expired_count += 1
                    logger.info(
                        "Expired reservation %s for %s (qty=%d)",
                        res.reservation_id, res.product_id, res.quantity,
                    )
        return expired_count

    def get_stock_snapshot(self) -> List[dict]:
        """Return current stock levels for metrics export."""
        with self._lock:
            return [
                {"product_id": p.product_id, "name": p.name, "available": p.available}
                for p in self._products.values()
            ]
