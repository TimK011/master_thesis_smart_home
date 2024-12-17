from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from utils import load_file
from ai_service import analyze_with_ai
import logging


# Initialize the FastAPI application with metadata
app = FastAPI(
    title="Smart Home Security Analysis API",
    description="API to integrate generative AI models for vulnerability analysis",
    version="1.0.0"
)

# Configure basic logging with INFO level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the main endpoint for analyzing data using AI
@app.post("/api/v1/analyze")
async def analyze(
    prompt: str = Form(...),
    file: UploadFile = File(...),
    provider: str = Query("openai", description="AI provider name (openai or gemini)"),
    file_format: str = Query(None, description="Optional: Specify the file format (json, xml, txt, csv)")
):
    # Log the incoming request
    logger.info("Received analyze request")
    logger.info(f"Filename: {file.filename}, Provider: {provider}, File_Format: {file_format}")

    # Load and parse the uploaded file using utility functions
    file_data = await load_file(file, file_format=file_format)
    if file_data is None:
        logger.error("Failed to parse file")
        raise HTTPException(status_code=400, detail="Could not parse the provided file.")

    logger.info("File parsed successfully. Sending data to AI provider.")
    result = await analyze_with_ai(prompt, file_data, provider)
    logger.info("Analysis complete")
    return {"analysis_result": result}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
