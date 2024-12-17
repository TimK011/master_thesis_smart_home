import logging
from fastapi import HTTPException
from config import OPENAI_API_KEY, GEMINI_API_KEY
import httpx

# Import the Gemini SDK for AI interactions
from google import genai

# Configure logging for this module
logger = logging.getLogger(__name__)

async def analyze_with_ai(prompt: str, file_data: dict, provider: str) -> str:
    """
    Analyze the provided data using the specified AI provider.

    Args:
        prompt (str): The user-provided prompt for the AI.
        file_data (dict): The data extracted from the uploaded file.
        provider (str): The AI provider to use ('openai' or 'gemini').

    Returns:
        str: The AI-generated analysis result.

    Raises:
        HTTPException: If there is an error communicating with the AI provider or if the provider is unsupported.
    """
    if provider == "openai":
        # Use OpenAI as the AI provider
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
            # Send the request to OpenAI's API asynchronously
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
            # Return the AI's response content
            return result["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                # Handle rate limit exceeded error
                logger.error("Rate limit exceeded. Please try again later.")
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait and try again.")
            else:
                # Handle other HTTP errors
                logger.error(f"Error calling AI provider: {e}")
                raise HTTPException(status_code=500, detail="Error communicating with AI provider")

    elif provider == "gemini":
        # Use Gemini as the AI provider
        if not GEMINI_API_KEY:
            # Check if the Gemini API key is configured
            logger.error("No Gemini API Key provided.")
            raise HTTPException(status_code=500, detail="Gemini API key not configured.")

        # Initialize the Gemini client with the API key
        client = genai.Client(api_key=GEMINI_API_KEY)

        # Combine the prompt and file data into a single string
        combined_content = f"{prompt}\nHere is the scan data: {file_data}"

        try:
            # Generate content using the Gemini 2.0 experimental model
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=combined_content
            )
            # Return the AI's response text
            return response.text
        except Exception as e:
            # Handle any exceptions during the Gemini API call
            logger.error(f"Error calling Gemini provider: {e}")
            raise HTTPException(status_code=500, detail="Error communicating with Gemini provider")

    else:
        # Handle unsupported AI providers
        logger.error(f"Unsupported provider: {provider}")
        raise HTTPException(status_code=400, detail="Unsupported provider")
