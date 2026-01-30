# Import OpenTelemetry instrumentation FIRST (side-effect initialization)
import app.otel_instrumentation  # noqa: F401

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.routes import auth, home, credito_hipotecario, tarjeta_credito

app = FastAPI(title="Fintech Demo", version="1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(home.router)
app.include_router(credito_hipotecario.router)
app.include_router(tarjeta_credito.router)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)