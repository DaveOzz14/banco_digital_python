from fastapi import APIRouter, Request
from app.core.templates import templates
import random
import time
import logging
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from app.otel_instrumentation import (
    payment_attempts_counter,
    payment_success_counter,
    payment_failure_counter,
    payment_duration_histogram
)

router = APIRouter(prefix="/tarjeta")
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

@router.get("/resumen")
def resumen(request: Request):
    """Display credit card summary."""
    with tracer.start_as_current_span(
        "view_credit_card_summary",
        attributes={
            "http.route": "/tarjeta/resumen",
            "ui.page": "tarjeta_resumen",
            "card.balance": 1_250_000,
            "card.minimum_payment": 320_000
        }
    ) as span:
        logger.info("Rendering credit card summary page")
        return templates.TemplateResponse(
            "tarjeta_resumen.html",
            {
                "request": request,
                "saldo": 1_250_000,
                "minimo": 320_000
            }
        )

@router.post("/pagar")
def pagar(request: Request):
    """Process credit card payment."""
    with tracer.start_as_current_span(
        "process_payment",
        attributes={
            "http.route": "/tarjeta/pagar",
            "payment.type": "credit_card",
            "payment.action": "pay"
        }
    ) as span:
        start_time = time.time()
        payment_attempts_counter.add(1, {"payment_type": "credit_card"})
        logger.info("Starting credit card payment processing")
        
        try:
            # Simulate gateway latency
            with tracer.start_as_current_span(
                "gateway_connection",
                attributes={"gateway.name": "payment_gateway"}
            ) as gateway_span:
                logger.info("Connecting to payment gateway")
                time.sleep(1.2)
                gateway_span.set_attribute("gateway.latency_ms", 1200)
            
            # Simulate gateway failure (always fails for demo)
            gateway_ok = False  # cámbialo a random.choice([True, False]) si quieres
            
            duration_ms = (time.time() - start_time) * 1000
            payment_duration_histogram.record(duration_ms, {"payment_type": "credit_card"})
            
            if not gateway_ok:
                payment_failure_counter.add(1, {"payment_type": "credit_card", "failure_reason": "gateway_error"})
                logger.error("Payment failed: Gateway connection error")
                span.set_attribute("payment.result", "failure")
                span.set_attribute("payment.failure_reason", "gateway_error")
                span.set_attribute("payment.duration_ms", duration_ms)
                span.set_status(Status(StatusCode.ERROR, "Gateway connection error"))
                
                return templates.TemplateResponse(
                    "tarjeta_error.html",
                    {
                        "request": request,
                        "mensaje": "No fue posible procesar el pago por error de conexión con el Gateway."
                    },
                    status_code=502
                )
            
            # Success path (not executed in demo)
            payment_success_counter.add(1, {"payment_type": "credit_card"})
            logger.info("Payment processed successfully")
            span.set_attribute("payment.result", "success")
            span.set_attribute("payment.duration_ms", duration_ms)
            span.set_status(Status(StatusCode.OK))
            
            return templates.TemplateResponse(
                "tarjeta_ok.html",
                {"request": request}
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            payment_duration_histogram.record(duration_ms, {"payment_type": "credit_card"})
            payment_failure_counter.add(1, {"payment_type": "credit_card", "failure_reason": "exception"})
            logger.error(f"Payment error: {str(e)}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise