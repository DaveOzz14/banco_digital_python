from fastapi import APIRouter, Request, Form
from app.core.templates import templates

router = APIRouter(prefix="/hipotecario")

@router.get("/solicitud")
def form(request: Request):
    return templates.TemplateResponse(
        "hipotecario_form.html",
        {"request": request}
    )

@router.post("/registrar")
def registrar(
    request: Request,
    nombre: str = Form(...),
    ingreso: float = Form(...),
    valor_vivienda: float = Form(...)
):
    # Simulación de registro exitoso
    return templates.TemplateResponse(
        "hipotecario_registro.html",
        {
            "request": request,
            "nombre": nombre,
            "ingreso": ingreso,
            "valor_vivienda": valor_vivienda,
            "estado": "RECIBIDA"
        }
    )
