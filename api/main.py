from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from utils import load_file
from ai_service import analyze_with_ai
import logging

app = FastAPI(
    title="Smart Home Security Analysis API",
    description="API to integrate generative AI models for vulnerability analysis",
    version="1.0.0"
)

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)

@app.post("/api/v1/analyze")
async def analyze(
    prompt: str = Form(...),
    file: UploadFile = File(...),
    provider: str = Query("openai", description="AI provider name (e.g. openai or gemini)")
):
    logging.info("Received analyze request")

    file_data = await load_file(file)
    if file_data is None:
        logging.error("Failed to parse file as JSON")
        raise HTTPException(status_code=400, detail="Could not parse the provided file as JSON.")

    logging.info(f"Analyzing with provider: {provider}")
    result = await analyze_with_ai(prompt, file_data, provider)
    logging.info("Analysis complete")
    return {"analysis_result": result}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
