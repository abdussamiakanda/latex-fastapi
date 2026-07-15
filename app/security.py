from fastapi import HTTPException, Request, status
from app.keys import get_active_keys, is_valid_key


async def verify_api_key(request: Request) -> None:
    active_keys = get_active_keys()
    if not active_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key verification is required but no keys are configured",
        )

    api_key: str | None = request.headers.get("X-API-Key")
    if api_key is None:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            api_key = auth_header[7:]

    if not is_valid_key(api_key or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
