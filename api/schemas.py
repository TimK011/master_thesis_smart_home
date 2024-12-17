from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    prompt: str
