# api.py
import os
from fastapi import FastAPI, Header, HTTPException, status, Depends

from run_tests import run_reliability_suite

app = FastAPI(title="QualiGenAI Reliability Engine Service")


async def verify_internal_key(x_internal_key: str = Header(...)):
    expected = os.getenv("INTERNAL_API_KEY")
    if not expected or x_internal_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing internal API key.")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "reliability-engine"}


@app.post("/run", dependencies=[Depends(verify_internal_key)])
async def run():
    """
    Runs the real reliability suite and returns the report directly —
    no file is read afterward, the response IS the result.
    """
    outcome = run_reliability_suite()
    return outcome