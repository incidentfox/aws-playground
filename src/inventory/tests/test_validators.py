# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for request validators."""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api.validators import validate_reserve_request, validate_release_request


class TestValidators(unittest.TestCase):

    def test_valid_reserve_request(self):
        self.assertIsNone(validate_reserve_request({"product_id": "ABC", "quantity": 3}))

    def test_reserve_missing_product_id(self):
        self.assertIsNotNone(validate_reserve_request({"quantity": 1}))

    def test_reserve_invalid_quantity(self):
        self.assertIsNotNone(validate_reserve_request({"product_id": "ABC", "quantity": -1}))

    def test_reserve_exceeds_max(self):
        self.assertIsNotNone(validate_reserve_request({"product_id": "ABC", "quantity": 100}))

    def test_valid_release_request(self):
        self.assertIsNone(validate_release_request({"product_id": "ABC", "quantity": 2}))

    def test_release_missing_product_id(self):
        self.assertIsNotNone(validate_release_request({}))


if __name__ == "__main__":
    unittest.main()
