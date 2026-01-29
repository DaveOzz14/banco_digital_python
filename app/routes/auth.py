from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.core.auth import validate_login
from app.core.templates import templates

router = APIRouter()

@router.get("/")
def login(request: Request):
    return templates.TemplateResponse(
        "login.html", {"request": request}
    )

@router.post("/login")
def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if validate_login(username, password):
        return RedirectResponse("/home", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Credenciales inválidas"}
    )
