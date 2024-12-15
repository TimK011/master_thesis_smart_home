from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from utils import load_file
from ai_service import analyze_with_ai
import logging

app = FastAPI(
    title="Smart Home Security Analysis API",
    description="API to integrate generative AI models for vulnerability analysis",
    version="1.0.0"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/v1/analyze")
async def analyze(
    prompt: str = Form(...),
    file: UploadFile = File(...),
    provider: str = Query("openai", description="AI provider name (e.g. openai or gemini)"),
    file_format: str = Query(None, description="Optional: Specify the file format (e.g. json, xml, txt)")
):
    logger.info("Received analyze request")
    logger.info(f"Filename: {file.filename}, Provider: {provider}, File_Format: {file_format}")

    file_data = await load_file(file, file_format=file_format)
    if file_data is None:
        logger.error("Failed to parse file")
        raise HTTPException(status_code=400, detail="Could not parse the provided file.")

    logger.info("File parsed successfully. Sending data to AI provider.")
    result = await analyze_with_ai(prompt, file_data, provider)
    logger.info("Analysis complete")
    return {"analysis_result": result}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
