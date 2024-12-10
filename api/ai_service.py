import httpx
from fastapi import HTTPException
from config import OPENAI_API_KEY, GEMINI_API_KEY

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
    elif provider == "gemini":
        api_key = GEMINI_API_KEY
        endpoint = "https://gemini.api.example/v1"
        payload = {
            "prompt": prompt,
            "data": file_data
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

    if provider == "openai":
        return result["choices"][0]["message"]["content"]
    else:
        return result.get("response", "No response")
