"""
Backend en Python (FastAPI) que actúa de intermediario seguro entre tu
frontend y la API de ElevenLabs Conversational AI.

Agentes configurados:
- Sunny (soporte de energías renovables) -> GET /api/get-signed-url
- Sam (mentor de Customer Success)        -> GET /api/sam/get-signed-url

La API key nunca sale del servidor: el frontend pide una "signed URL"
a este backend y con ella abre la conversación por WebSocket.
"""

import os
import logging

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AGENT_ID = os.getenv("AGENT_ID", "agent_2501m0zg0v8dftyv50v9wv5y6d4f")  # Sunny
SAM_AGENT_ID = os.getenv("SAM_AGENT_ID")  # Sam
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1/convai"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("elevenlabs-backend")

if not ELEVENLABS_API_KEY:
    logger.warning(
        "ELEVENLABS_API_KEY no está definida. Crea un archivo .env "
        "a partir de .env.example y añade tu API key real."
    )

if not SAM_AGENT_ID:
    logger.warning("SAM_AGENT_ID no está definida. La ruta de Sam no funcionará.")

app = FastAPI(title="ElevenLabs Agent Backend")

# En producción, cambia "*" por el dominio exacto de tu frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def obtener_signed_url(agent_id: str, nombre_agente: str):
    """
    Pide a ElevenLabs una signed URL de un solo uso para el agente indicado.
    La usan tanto Sunny como Sam.
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Falta ELEVENLABS_API_KEY en el servidor (revisa tu .env).",
        )

    if not agent_id:
        raise HTTPException(
            status_code=500,
            detail=f"Falta el ID del agente {nombre_agente} en el servidor.",
        )

    try:
        response = requests.get(
            f"{ELEVENLABS_BASE_URL}/conversation/get-signed-url",
            params={"agent_id": agent_id},
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Error al obtener la signed URL de %s: %s", nombre_agente, exc)
        raise HTTPException(
            status_code=502,
            detail=f"No se pudo obtener la signed URL de {nombre_agente}.",
        ) from exc

    data = response.json()
    return {"signedUrl": data["signed_url"]}


@app.get("/api/get-signed-url")
def get_signed_url():
    """Signed URL para Sunny (se mantiene igual para no romper la web de Sunny)."""
    return obtener_signed_url(AGENT_ID, "Sunny")


@app.get("/api/sam/get-signed-url")
def get_signed_url_sam():
    """Signed URL para Sam, el mentor de Customer Success."""
    return obtener_signed_url(SAM_AGENT_ID, "Sam")


@app.get("/api/calcular-ahorro")
def calcular_ahorro(factura_mensual: float):
    """
    Recibe la factura mensual de luz (en euros) y devuelve un ahorro
    estimado ficticio con paneles solares. (Herramienta de Sunny)
    """
    ahorro_mensual = round(factura_mensual * 0.85, 2)
    ahorro_anual = round(ahorro_mensual * 12, 2)
    paneles_recomendados = max(4, round(factura_mensual / 15))

    return {
        "factura_mensual": factura_mensual,
        "ahorro_mensual_estimado": ahorro_mensual,
        "ahorro_anual_estimado": ahorro_anual,
        "paneles_recomendados": paneles_recomendados,
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "agents": {
            "sunny": AGENT_ID,
            "sam": SAM_AGENT_ID or "no configurado",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=True)