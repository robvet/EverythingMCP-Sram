from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if not API_KEY:
        raise HTTPException(
            status_code=500, detail="API key not configured"
        )
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate API key"
        )