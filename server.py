"""
Backend en Python (FastAPI) que actúa de intermediario seguro entre tu
frontend y la API de ElevenLabs Conversational AI.

Qué hace:
- Expone un endpoint GET /api/get-signed-url
- Ese endpoint llama a la API de ElevenLabs con tu API key (que nunca
  sale del servidor) y le pide una "signed URL" para tu agente.
- El frontend (web, app, etc.) llama a este endpoint, recibe la
  signed URL y con ella abre la conversación por WebSocket, sin que
  la API key toque nunca el navegador/cliente.

Agente configurado: agent_2501m0zg0v8dftyv50v9wv5y6d4f
(puedes cambiarlo con la variable de entorno AGENT_ID si en el futuro
usas otro agente)
"""

import os
import logging

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
AGENT_ID = os.getenv("AGENT_ID", "agent_2501m0zg0v8dftyv50v9wv5y6d4f")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1/convai"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("elevenlabs-backend")

if not ELEVENLABS_API_KEY:
    logger.warning(
        "ELEVENLABS_API_KEY no está definida. Crea un archivo .env "
        "a partir de .env.example y añade tu API key real."
    )

app = FastAPI(title="ElevenLabs Agent Backend")

# En producción, cambia "*" por el dominio exacto de tu frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/get-signed-url")
def get_signed_url():
    """
    Devuelve una signed URL válida y de un solo uso para iniciar una
    conversación de voz con el agente, sin exponer la API key.
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Falta ELEVENLABS_API_KEY en el servidor (revisa tu .env).",
        )

    try:
        response = requests.get(
            f"{ELEVENLABS_BASE_URL}/conversation/get-signed-url",
            params={"agent_id": AGENT_ID},
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logger.error("Error al obtener la signed URL: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="No se pudo obtener la signed URL de ElevenLabs.",
        ) from exc

    data = response.json()
    return {"signedUrl": data["signed_url"]}

@app.get("/api/calcular-ahorro")
def calcular_ahorro(factura_mensual: float):
    """
    Recibe la factura mensual de luz (en euros) y devuelve un ahorro
    estimado ficticio con paneles solares.
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
    return {"status": "ok", "agent_id": AGENT_ID}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=3001, reload=True)
