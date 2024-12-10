import json
from typing import Optional, Any, Dict
from fastapi import UploadFile

async def load_file(file: UploadFile) -> Optional[Dict[str, Any]]:
    content = await file.read()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None
