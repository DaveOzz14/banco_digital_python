from fastapi import APIRouter, Request
from app.core.templates import templates
import random
import time

router = APIRouter(prefix="/tarjeta")

@router.get("/resumen")
def resumen(request: Request):
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
    # Simula latencia de gateway
    time.sleep(1.2)

    # Simula caída de gateway (siempre falla para demo)
    gateway_ok = False  # cámbialo a random.choice([True, False]) si quieres

    if not gateway_ok:
        return templates.TemplateResponse(
            "tarjeta_error.html",
            {
                "request": request,
                "mensaje": "No fue posible procesar el pago por error de conexión con el Gateway."
            },
            status_code=502
        )

    # (No se ejecuta en este demo)
    return templates.TemplateResponse(
        "tarjeta_ok.html",
        {"request": request}
    )
