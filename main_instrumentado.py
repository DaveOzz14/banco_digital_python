from fastapi import FastAPI
import uvicorn

# -----------------------------
# IMPORTS OPEN TELEMETRY
# -----------------------------

from opentelemetry import trace  
# Esta línea importa la API de trazas. 
# Permite obtener el tracer global y crear spans manuales.

from opentelemetry.sdk.resources import Resource  
# Permite definir los metadatos del servicio (service.name, version, environment).
# Estos datos identifican el servicio en Dynatrace.

from opentelemetry.sdk.trace import TracerProvider  
# Es el motor principal de tracing.
# Se encarga de crear tracers y gestionar la generación de spans.

from opentelemetry.sdk.trace.export import BatchSpanProcessor  
# Procesador que agrupa varios spans antes de enviarlos.
# Mejora rendimiento al enviar datos en lotes (batch).

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  
# Exportador que envía las trazas usando el protocolo estándar OTLP vía HTTP.
# Es el componente que envía la telemetría a Dynatrace.

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  
# Instrumentación automática para FastAPI.
# Crea spans automáticamente por cada request HTTP entrante.

from opentelemetry.instrumentation.uvicorn import UvicornInstrumentor  
# Instrumenta el servidor Uvicorn.
# Permite capturar correctamente el ciclo de vida de las peticiones ASGI.

# ----------------------------------------
# CONFIGURACIÓN OPEN TELEMETRY
# ----------------------------------------

resource = Resource(attributes={
    "service.name": "fastapi-ejemplo-dynatrace",  
    # Nombre del servicio que aparecerá en Dynatrace.
    
    "service.version": "1.0.0",  
    # Versión del servicio para trazabilidad de releases.
    
    "deployment.environment": "dev"  
    # Entorno donde corre el servicio (dev, qa, prod).
})

trace.set_tracer_provider(TracerProvider(resource=resource))  
# Inicializa el TracerProvider global y le asigna el Resource configurado.
# Sin esto, los spans no tendrían identidad de servicio.

tracer = trace.get_tracer(__name__)  
# Obtiene un tracer para este módulo.
# Este objeto permite crear spans manuales dentro del código.

# Endpoint OTLP Dynatrace (EJEMPLO)
OTLP_ENDPOINT = "https://abc123.live.dynatrace.com/api/v2/otlp/v1/traces"  
# Define el endpoint OTLP al que se enviarán las trazas (Dynatrace en este caso).

OTLP_HEADERS = {
    "Authorization": "Api-Token dt0c01.XXXXXXXXXXXX"
}
# Define los headers necesarios para autenticarse contra Dynatrace.
# Se usa un API Token con permisos de ingestión de trazas.

otlp_exporter = OTLPSpanExporter(
    endpoint=OTLP_ENDPOINT,
    headers=OTLP_HEADERS
)
# Crea el exportador OTLP.
# Este objeto es el encargado de enviar los spans al backend.

span_processor = BatchSpanProcessor(otlp_exporter)
# Crea un procesador de spans en modo batch.
# Agrupa los spans y los envía periódicamente al exportador.

trace.get_tracer_provider().add_span_processor(span_processor)
# Registra el BatchSpanProcessor en el TracerProvider.
# Esto conecta la generación de spans con el exportador hacia Dynatrace.

# ----------------------------------------
# FASTAPI
# ----------------------------------------

app = FastAPI(
    title="Aplicacion en Python",
    description="Ejercicio basico en Python"
)

# Instrumentación automática
FastAPIInstrumentor.instrument_app(app)
# Activa la instrumentación automática de FastAPI.
# Cada endpoint generará automáticamente un span HTTP.

UvicornInstrumentor().instrument()
# Instrumenta el servidor Uvicorn.
# Permite capturar correctamente el contexto y propagación de trazas.

@app.get("/")
def inicio():
    return {"mensaje": "Hola soy el endpoint raiz"}

@app.get("/sumar")
def sumar(a: int, b: int):

    with tracer.start_as_current_span("calculo_suma") as span:
        # Crea un span manual llamado "calculo_suma".
        # Este span será hijo del span HTTP generado automáticamente.

        resultado = a + b

        span.set_attribute("app.operacion", "suma")
        # Agrega un atributo personalizado al span.

        span.set_attribute("app.a", a)
        # Agrega el valor del parámetro 'a' como metadata del span.

        span.set_attribute("app.b", b)
        # Agrega el valor del parámetro 'b' como metadata del span.

        return {
            "operacion": "Suma",
            "a": a,
            "b": b,
            "resultado": resultado
        }

@app.get("/operacion")
def operacion(a: int, b: int, tipo: str):

    with tracer.start_as_current_span("calculo_operacion") as span:
        # Crea un span manual para esta operación.

        span.set_attribute("app.tipo_operacion", tipo)
        # Guarda el tipo de operación como atributo del span.

        if tipo == "suma":
            resultado = a + b
        elif tipo == "resta":
            resultado = a - b
        elif tipo == "multiplicacion":
            resultado = a * b
        elif tipo == "division":
            resultado = a / b
        else:
            resultado = "Ninguna Operacion"

        return {
            "operacion": tipo,
            "resultado": resultado
        }

@app.get("/tabla")
def tabla(numero: int):

    with tracer.start_as_current_span("calculo_tabla") as span:
        # Crea un span manual para el cálculo de la tabla.

        span.set_attribute("app.numero", numero)
        # Guarda el número recibido como atributo del span.

        resultados = []

        for i in range(1, 11):
            resultados.append({
                "resultado": numero * i
            })

        return {
            "numero": numero,
            "tabla": resultados
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


#dt0c01.NVWZ3DBAR52MJHSIJQ53SIWL.XFU6DL4L2CO5OIAZVUPO47UQB2WLMANA3I545MSOGF2WEEH6KU2D7GBUUR667XED
 
#https://lqb55772.apps.dynatrace.com/
