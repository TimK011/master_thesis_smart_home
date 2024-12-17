import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Retrieve the API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
