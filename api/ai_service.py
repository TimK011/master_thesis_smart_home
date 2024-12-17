import logging
from fastapi import HTTPException
from config import OPENAI_API_KEY, GEMINI_API_KEY
import httpx

# Neuer Import für das Gemini SDK
from google import genai

logger = logging.getLogger(__name__)

async def analyze_with_ai(prompt: str, file_data: dict, provider: str) -> str:
    if provider == "openai":
        api_key = OPENAI_API_KEY
        endpoint = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a security expert analyzing smart home vulnerabilities."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"Here is the scan data: {file_data}"}
            ]
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
            return result["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                logger.error("Rate limit exceeded. Please try again later.")
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and try again.")
            else:
                logger.error(f"Error calling AI provider: {e}")
                raise HTTPException(status_code=500, detail="Error communicating with AI provider")

    elif provider == "gemini":
        if not GEMINI_API_KEY:
            logger.error("No Gemini API Key provided.")
            raise HTTPException(status_code=500, detail="Gemini API key not configured.")

        # Initialisiere den Gemini-Client
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Kombinieren von Prompt und File-Daten in einen String.
        # Sie können diesen je nach Bedarf anpassen.
        combined_content = f"{prompt}\nHere is the scan data: {file_data}"

        try:
            # Nutzung des Gemini 2.0 Modells (experimental)
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=combined_content
            )
            return response.text
        except Exception as e:
            # Hier können Sie weitere Fehlerbehandlung einbauen, falls nötig.
            logger.error(f"Error calling Gemini provider: {e}")
            raise HTTPException(status_code=500, detail="Error communicating with Gemini provider")

    else:
        logger.error(f"Unsupported provider: {provider}")
        raise HTTPException(status_code=400, detail="Unsupported provider")
