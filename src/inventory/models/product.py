# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Product and stock-level domain models."""

from dataclasses import dataclass, field
from enum import Enum


class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


@dataclass
class Product:
    product_id: str
    name: str
    quantity: int
    reserved: int = 0
    warehouse: str = "us-west-2a"

    @property
    def available(self) -> int:
        return max(0, self.quantity - self.reserved)

    @property
    def status(self) -> StockStatus:
        if self.available <= 0:
            return StockStatus.OUT_OF_STOCK
        elif self.available < 10:
            return StockStatus.LOW_STOCK
        return StockStatus.IN_STOCK

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "reserved": self.reserved,
            "available": self.available,
            "status": self.status.value,
            "warehouse": self.warehouse,
        }
