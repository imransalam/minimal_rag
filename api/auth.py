from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")
SECRET_API_KEY = os.getenv("API_AUTH_KEY", "default_secret_key_if_not_set")

async def check_key(api_key: str = Depends(api_key_header)):
    if api_key == SECRET_API_KEY:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
        headers={"WWW-Authenticate": "X-API-Key"},
    )
