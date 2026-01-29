from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import auth, home, credito_hipotecario, tarjeta_credito

app = FastAPI(title="Fintech Demo", version="1.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(home.router)
app.include_router(credito_hipotecario.router)
app.include_router(tarjeta_credito.router)
