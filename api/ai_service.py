import logging
from fastapi import HTTPException
from config import OPENAI_API_KEY, GEMINI_API_KEY
import httpx
from typing_extensions import TypedDict
from typing import List

# Simplify the schema: just use str for severity to avoid potential issues.
class Vulnerability(TypedDict):
    vulnerability_name: str
    description: str
    severity: str
    remediation: str

logger = logging.getLogger(__name__)

async def analyze_with_ai(prompt: str, file_data: dict, provider: str) -> str:
    if provider == "openai":
        json_schema_description = """Please return the vulnerabilities as a valid JSON list in the following format:
[
  {
    "vulnerability_name": "string",
    "description": "string",
    "severity": "low|medium|high",
    "remediation": "string describing how to fix the vulnerability"
  }
]

Do not include any additional text, explanation, or commentary outside the JSON.
"""

        combined_prompt = f"""{prompt}

Here is the scan data: {file_data}

{json_schema_description}
"""

        endpoint = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a security expert analyzing smart home vulnerabilities."},
                {"role": "user", "content": combined_prompt}
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
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
                logger.error("Rate limit exceeded for OpenAI. Please try again later.")
                raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded. Please wait and try again.")
            else:
                logger.error(f"Error calling OpenAI provider: {e}")
                raise HTTPException(status_code=500, detail="Error communicating with OpenAI provider")

    elif provider == "gemini":
        if not GEMINI_API_KEY:
            logger.error("No Gemini API Key provided.")
            raise HTTPException(status_code=500, detail="Gemini API key not configured.")

        import google.generativeai as genai

        combined_content = f"""{prompt}

Here is the scan data: {file_data}

Please return the vulnerabilities as a JSON list in this format:
[
  {{
    "vulnerability_name": "string",
    "description": "string",
    "severity": "low|medium|high",
    "remediation": "string describing how to fix the vulnerability"
  }}
]
"""

        # Use 'list[Vulnerability]' instead of 'List[Vulnerability]'
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=list[Vulnerability]  # Changed here
        )

        try:
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(
                contents=combined_content,
                generation_config=generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini provider: {e}")
            raise HTTPException(status_code=500, detail="Error communicating with Gemini provider")

    else:
        logger.error(f"Unsupported provider: {provider}")
        raise HTTPException(status_code=400, detail="Unsupported provider")
