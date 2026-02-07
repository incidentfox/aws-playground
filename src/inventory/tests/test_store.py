# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for the in-memory inventory store."""

import sys
import os
import unittest

# Allow imports from the service root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.product import StockStatus
from store.memory import InMemoryInventoryStore


class TestInMemoryInventoryStore(unittest.TestCase):

    def setUp(self):
        self.store = InMemoryInventoryStore(reservation_ttl_seconds=1)

    def test_list_products_returns_catalog(self):
        products = self.store.list_products()
        self.assertEqual(len(products), 10)

    def test_get_product_found(self):
        product = self.store.get_product("OLJCESPC7Z")
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "National Park Foundation Explorascope")

    def test_get_product_not_found(self):
        product = self.store.get_product("NONEXISTENT")
        self.assertIsNone(product)

    def test_reserve_success(self):
        reservation = self.store.reserve("OLJCESPC7Z", 5)
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.quantity, 5)

        product = self.store.get_product("OLJCESPC7Z")
        self.assertEqual(product.available, 95)

    def test_reserve_insufficient_stock(self):
        reservation = self.store.reserve("9SIQT8TOJO", 9999)
        self.assertIsNone(reservation)

    def test_reserve_unknown_product(self):
        reservation = self.store.reserve("NONEXISTENT", 1)
        self.assertIsNone(reservation)

    def test_release_stock(self):
        self.store.reserve("OLJCESPC7Z", 10)
        product = self.store.get_product("OLJCESPC7Z")
        self.assertEqual(product.available, 90)

        self.store.release("OLJCESPC7Z", 5)
        product = self.store.get_product("OLJCESPC7Z")
        self.assertEqual(product.available, 95)

    def test_stock_status(self):
        product = self.store.get_product("9SIQT8TOJO")  # qty=25
        self.assertEqual(product.status, StockStatus.IN_STOCK)

        # Reserve almost everything
        self.store.reserve("9SIQT8TOJO", 20)
        product = self.store.get_product("9SIQT8TOJO")
        self.assertEqual(product.status, StockStatus.LOW_STOCK)

        # Reserve the rest
        self.store.reserve("9SIQT8TOJO", 5)
        product = self.store.get_product("9SIQT8TOJO")
        self.assertEqual(product.status, StockStatus.OUT_OF_STOCK)


if __name__ == "__main__":
    unittest.main()
