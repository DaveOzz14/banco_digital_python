"""OpenTelemetry Instrumentation Bootstrap

This module initializes all OpenTelemetry components (traces, metrics, logs)
and must be imported as a side-effect at application startup.

Configuration is read exclusively from environment variables:
- OTEL_EXPORTER_OTLP_PROTOCOL
- OTEL_EXPORTER_OTLP_ENDPOINT
- OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
- OTEL_EXPORTER_OTLP_METRICS_ENDPOINT
- OTEL_EXPORTER_OTLP_LOGS_ENDPOINT
- OTEL_EXPORTER_OTLP_HEADERS
- OTEL_SERVICE_NAME
- OTEL_RESOURCE_ATTRIBUTES
"""

import os
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

# Parse resource attributes from environment
def parse_resource_attributes():
    """Parse OTEL_RESOURCE_ATTRIBUTES environment variable."""
    attrs = {}
    resource_attrs_str = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
    if resource_attrs_str:
        for pair in resource_attrs_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                attrs[key.strip()] = value.strip()
    return attrs

# Build resource
resource_attrs = parse_resource_attributes()
resource = Resource.create(
    {
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "banco_digital_observability"),
        SERVICE_VERSION: resource_attrs.get("service.version", "1.0.0"),
        DEPLOYMENT_ENVIRONMENT: resource_attrs.get("deployment.environment", "production"),
    }
)

# Parse OTLP headers
def parse_otlp_headers():
    """Parse OTEL_EXPORTER_OTLP_HEADERS environment variable."""
    headers_dict = {}
    headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    if headers_str:
        for pair in headers_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                headers_dict[key.strip()] = value.strip()
    return headers_dict

otlp_headers = parse_otlp_headers()

# ============ TRACES ============
trace_endpoint = os.getenv(
    "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
    os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://otlp-gateway-prod-us-east-2.grafana.net/otlp") + "/v1/traces"
)

span_exporter = OTLPSpanExporter(
    endpoint=trace_endpoint,
    headers=otlp_headers
)

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)

# Export tracer for manual instrumentation
tracer = trace.get_tracer(__name__)

# ============ METRICS ============
metric_endpoint = os.getenv(
    "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
    os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://otlp-gateway-prod-us-east-2.grafana.net/otlp") + "/v1/metrics"
)

metric_exporter = OTLPMetricExporter(
    endpoint=metric_endpoint,
    headers=otlp_headers
)

metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=60000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Export meter for manual instrumentation
meter = metrics.get_meter(__name__)

# Create business metrics
login_counter = meter.create_counter(
    name="banco_digital.login.attempts",
    description="Number of login attempts",
    unit="1"
)

login_success_counter = meter.create_counter(
    name="banco_digital.login.success",
    description="Number of successful logins",
    unit="1"
)

login_failure_counter = meter.create_counter(
    name="banco_digital.login.failure",
    description="Number of failed logins",
    unit="1"
)

payment_attempts_counter = meter.create_counter(
    name="banco_digital.payment.attempts",
    description="Number of payment attempts",
    unit="1"
)

payment_success_counter = meter.create_counter(
    name="banco_digital.payment.success",
    description="Number of successful payments",
    unit="1"
)

payment_failure_counter = meter.create_counter(
    name="banco_digital.payment.failure",
    description="Number of failed payments",
    unit="1"
)

payment_duration_histogram = meter.create_histogram(
    name="banco_digital.payment.duration",
    description="Payment processing duration",
    unit="ms"
)

# ============ LOGS ============
log_endpoint = os.getenv(
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
    os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://otlp-gateway-prod-us-east-2.grafana.net/otlp") + "/v1/logs"
)

log_exporter = OTLPLogExporter(
    endpoint=log_endpoint,
    headers=otlp_headers
)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
set_logger_provider(logger_provider)

# Configure Python logging to use OpenTelemetry
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

# Export logger for manual logging
logger = logging.getLogger(__name__)