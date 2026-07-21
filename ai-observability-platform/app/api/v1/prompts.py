# app/api/v1/prompts.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.core.database import get_db_connection
from app.core.security import verify_internal_key

router = APIRouter(prefix="/prompts", tags=["Prompt Version Control"])


class PromptCheckIn(BaseModel):
    prompt_name: str
    prompt_hash: str
    prompt_text: str
    author: str = "Rambhupal"


@router.post("/check-in", dependencies=[Depends(verify_internal_key)])
async def check_in_prompt(payload: PromptCheckIn):
    """
    Called by RAG / Pilgrim Bot with their own computed hash. Only inserts
    a new version row if the hash actually changed since the last one.
    """
    try:
        with get_db_connection() as conn:
            latest = conn.execute(
                "SELECT prompt_hash, version_tag FROM prompt_registry "
                "WHERE prompt_name = ? ORDER BY changed_at DESC LIMIT 1",
                [payload.prompt_name]
            ).fetchone()

            if latest is None:
                new_version, parent_hash = "v1", None
            elif latest[0] == payload.prompt_hash:
                return {"changed": False, "version_tag": latest[1]}
            else:
                parent_hash = latest[0]
                try:
                    prev_num = int(latest[1].lstrip("v"))
                except (ValueError, AttributeError):
                    prev_num = 0
                new_version = f"v{prev_num + 1}"

            conn.execute(
                """
                INSERT INTO prompt_registry
                    (prompt_hash, prompt_name, version_tag, prompt_text, author, changed_at, parent_hash)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """,
                [payload.prompt_hash, payload.prompt_name, new_version, payload.prompt_text, payload.author, parent_hash]
            )
            return {"changed": True, "version_tag": new_version}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history", dependencies=[Depends(verify_internal_key)])
async def get_prompt_history():
    """Returns full prompt version history for the Control Hub dashboard."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT prompt_name, version_tag, author, changed_at "
                "FROM prompt_registry ORDER BY changed_at DESC"
            ).fetchall()
        return {
            "history": [
                {"prompt_name": r[0], "version_tag": r[1], "author": r[2], "changed_at": str(r[3])}
                for r in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))