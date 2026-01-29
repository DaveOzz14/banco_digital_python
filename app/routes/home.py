from fastapi import APIRouter, Request
from app.core.templates import templates

router = APIRouter()

@router.get("/home")
def home(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request}
    )
