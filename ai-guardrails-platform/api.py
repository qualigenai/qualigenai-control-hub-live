# api.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, status, Depends

load_dotenv()

from run_guardrail_tests import run_guardrail_suite

app = FastAPI(title="QualiGenAI Guardrails Platform Service")


async def verify_internal_key(x_internal_key: str = Header(...)):
    expected = os.getenv("INTERNAL_API_KEY")
    if not expected or x_internal_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing internal API key.")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "guardrails-platform"}


@app.post("/run", dependencies=[Depends(verify_internal_key)])
async def run():
    """
    Runs the real guardrail suite and returns the report directly.
    """
    outcome = run_guardrail_suite()
    return outcome