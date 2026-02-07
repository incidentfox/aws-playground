# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Client for the product-catalog gRPC service."""

import logging

import grpc
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class ProductCatalogClient:
    """Fetches product metadata from the product-catalog service.

    Used to sync the inventory catalog with the canonical product list.
    In the current version, the catalog is seeded at startup; this client
    is wired up for future use when live sync is needed.
    """

    def __init__(self, address: str):
        self._address = address
        self._channel = None

    def connect(self):
        self._channel = grpc.insecure_channel(self._address)
        logger.info("Connected to product-catalog at %s", self._address)

    def close(self):
        if self._channel:
            self._channel.close()

    def list_products(self):
        """Fetch all products from the catalog.

        Returns a list of product dicts with id and name.
        """
        with tracer.start_as_current_span("product_catalog.list_products") as span:
            span.set_attribute("rpc.system", "grpc")
            span.set_attribute("rpc.service", "oteldemo.ProductCatalogService")
            span.set_attribute("rpc.method", "ListProducts")
            span.set_attribute("server.address", self._address)

            # Stub: in production this would call the gRPC endpoint.
            # For now the catalog is seeded from the known product list.
            logger.debug("product_catalog.list_products called (stub)")
            return []
