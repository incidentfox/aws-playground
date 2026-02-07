# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

"""OpenTelemetry provider initialization for traces, metrics, and logs."""

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

_tracer = None
_meter = None


def init_telemetry(service_name: str, service_version: str, namespace: str,
                   otel_endpoint: str, insecure: bool = True):
    """Initialize OpenTelemetry providers for traces and metrics."""
    global _tracer, _meter

    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: service_version,
        "service.namespace": namespace,
    })

    # Traces
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=otel_endpoint, insecure=insecure)
        )
    )
    trace.set_tracer_provider(trace_provider)
    _tracer = trace.get_tracer(service_name, service_version)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otel_endpoint, insecure=insecure),
        export_interval_millis=60000,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(service_name, service_version)

    return _tracer, _meter


def get_tracer():
    if _tracer is None:
        raise RuntimeError("Telemetry not initialized. Call init_telemetry() first.")
    return _tracer


def get_meter():
    if _meter is None:
        raise RuntimeError("Telemetry not initialized. Call init_telemetry() first.")
    return _meter
