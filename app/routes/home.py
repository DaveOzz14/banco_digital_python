from fastapi import APIRouter, Request
from app.core.templates import templates
import logging
from opentelemetry import trace

router = APIRouter()
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

@router.get("/home")
def home(request: Request):
    """Render home page after successful login."""
    with tracer.start_as_current_span(
        "render_home_page",
        attributes={
            "http.route": "/home",
            "ui.page": "home"
        }
    ) as span:
        logger.info("Rendering home page")
        return templates.TemplateResponse(
            "home.html", {"request": request}
        )