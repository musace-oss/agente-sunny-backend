# Sunny – Voice support agent for a renewable energy company

Sunny is a voice assistant I built to learn how conversational AI works in a customer support setting. It answers questions for **Aurora Renovables**, a fictional renewable energy company, and can estimate how much a customer could save with solar energy.

This repository contains the backend that connects the agent to the website, plus a small public demo page.

## What Sunny can do

- Answer customer questions using a knowledge base (a fictional product catalog for Aurora Renovables).
- Calculate estimated savings through a custom tool (`calcular_ahorro`) that calls an endpoint on this backend.
- Talk with users by voice from a web page, using the ElevenLabs widget.

## How it works

1. The web page loads the ElevenLabs Conversational AI widget.
2. Instead of exposing the API key in the browser, the page asks this backend for a **signed URL**. The backend generates it with the API key, which stays on the server.
3. When a customer asks about savings, the agent calls the `calcular_ahorro` endpoint and uses the result in its answer.

## Tech stack

- **ElevenLabs Conversational AI** – voice agent, knowledge base and tools
- **Python + FastAPI** – backend
- **Render** – hosting for the backend
- **HTML** – test pages and public demo page
- **Git / GitHub** – version control

## Project structure

| File / folder | What it is |
|---|---|
| `server.py` | FastAPI backend: signed URL generation and the `calcular_ahorro` endpoint |
| `site/` | Public demo page |
| `test_client.html` | Page for testing the backend locally |
| `widget_test.html` | Page for testing the ElevenLabs widget |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variables needed (without real values) |

## Run it locally

1. Clone the repository.
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your own values.
4. Start the server:
   ```
   uvicorn server:app --reload
   ```

## What I learned

- How to give a voice agent a knowledge base and custom tools.
- How to keep API keys secure with a backend and signed URLs.
- How to deploy a Python backend with Render.
- Working with Git and GitHub from VS Code.

## Next steps

- Review conversation analytics to improve the agent's answers.
- Connect a real phone number.
- Build a second agent.

---

Built by Sandra Ceceñas · [LinkedIn](https://www.linkedin.com/in/sandra-luc%C3%ADa-cece%C3%B1as-amador-542756155/)
