import os
from fastapi import Header, HTTPException, status


async def verify_internal_key(x_internal_key: str = Header(...)):
    expected = os.getenv("INTERNAL_API_KEY")
    if not expected or x_internal_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal API key.",
        )