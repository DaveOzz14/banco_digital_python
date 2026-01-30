from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.core.auth import validate_login
from app.core.templates import templates
import logging
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from app.otel_instrumentation import login_counter, login_success_counter, login_failure_counter

router = APIRouter()
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

@router.get("/")
def login(request: Request):
    """Render login page."""
    with tracer.start_as_current_span(
        "render_login_page",
        attributes={
            "http.route": "/",
            "ui.page": "login"
        }
    ) as span:
        logger.info("Rendering login page")
        return templates.TemplateResponse(
            "login.html", {"request": request}
        )

@router.post("/login")
def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Process login form submission."""
    with tracer.start_as_current_span(
        "user_login",
        attributes={
            "http.route": "/login",
            "user.username": username,
            "auth.action": "login"
        }
    ) as span:
        login_counter.add(1, {"username": username})
        logger.info(f"Login attempt for user: {username}")
        
        try:
            if validate_login(username, password):
                login_success_counter.add(1, {"username": username})
                logger.info(f"Login successful for user: {username}")
                span.set_attribute("auth.result", "success")
                span.set_status(Status(StatusCode.OK))
                return RedirectResponse("/home", status_code=302)
            
            login_failure_counter.add(1, {"username": username})
            logger.warning(f"Login failed for user: {username} - Invalid credentials")
            span.set_attribute("auth.result", "failure")
            span.set_attribute("auth.failure_reason", "invalid_credentials")
            span.set_status(Status(StatusCode.ERROR, "Invalid credentials"))
            
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Credenciales inválidas"}
            )
        except Exception as e:
            login_failure_counter.add(1, {"username": username})
            logger.error(f"Login error for user {username}: {str(e)}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise