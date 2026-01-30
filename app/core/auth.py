import logging
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

def validate_login(username: str, password: str) -> bool:
    """Validate user credentials."""
    with tracer.start_as_current_span(
        "validate_credentials",
        attributes={
            "auth.username": username,
            "auth.method": "password"
        }
    ) as span:
        # Login fake, solo demo
        is_valid = username == "admin" and password == "1234"
        
        if is_valid:
            logger.info(f"Credentials validated successfully for user: {username}")
            span.set_attribute("auth.validation_result", "valid")
            span.set_status(Status(StatusCode.OK))
        else:
            logger.warning(f"Invalid credentials for user: {username}")
            span.set_attribute("auth.validation_result", "invalid")
            span.set_status(Status(StatusCode.ERROR, "Invalid credentials"))
        
        return is_valid