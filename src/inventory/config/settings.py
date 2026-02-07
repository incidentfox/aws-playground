# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Application configuration loaded from environment variables."""

import os


class Settings:
    SERVICE_NAME: str = os.getenv("OTEL_SERVICE_NAME", "inventory")
    SERVICE_VERSION: str = "0.1.0"
    SERVICE_NAMESPACE: str = "opentelemetry-demo"

    # Server
    HOST: str = os.getenv("INVENTORY_SERVICE_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("INVENTORY_SERVICE_PORT", "8080"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # OpenTelemetry
    OTEL_ENDPOINT: str = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
    )
    OTEL_INSECURE: bool = os.getenv("OTEL_INSECURE", "true").lower() == "true"

    # Upstream services
    PRODUCT_CATALOG_ADDR: str = os.getenv(
        "PRODUCT_CATALOG_SERVICE_ADDR", "product-catalog:8080"
    )

    # Inventory thresholds
    LOW_STOCK_THRESHOLD: int = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))
    REORDER_POINT: int = int(os.getenv("REORDER_POINT", "20"))
    MAX_RESERVATION_QTY: int = int(os.getenv("MAX_RESERVATION_QTY", "50"))
    RESERVATION_TTL_SECONDS: int = int(os.getenv("RESERVATION_TTL_SECONDS", "900"))


settings = Settings()
