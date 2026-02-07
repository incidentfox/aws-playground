# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""Background worker that expires stale reservations and releases stock."""

import logging
import threading
import time

from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class ReservationExpiryWorker:
    """Periodically scans for expired reservations and releases their stock."""

    def __init__(self, store, interval_seconds: int = 60):
        self._store = store
        self._interval = interval_seconds
        self._thread = None
        self._stop_event = threading.Event()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Reservation expiry worker started (interval=%ds)", self._interval)

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        while not self._stop_event.is_set():
            try:
                with tracer.start_as_current_span("expire_reservations"):
                    expired = self._store.expire_reservations()
                    if expired > 0:
                        logger.info("Expired %d stale reservations", expired)
            except Exception:
                logger.exception("Error in reservation expiry worker")

            self._stop_event.wait(self._interval)
