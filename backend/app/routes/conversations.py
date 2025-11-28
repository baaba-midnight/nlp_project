"""Conversation routes for single-user chatbot.

Endpoints:
- GET /conversations
- POST /conversations
- GET /conversations/{conversation_id}/messages
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from ..db import supabase
from ..models.conversations import ConversationOut, MessageCreate

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationOut])
def list_conversations(limit: int = 50, offset: int = 0):
    try:
        resp = (
            supabase.table("conversations")
            .select("*")
            .order("last_active_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ConversationOut)
def create_conversation(
    title: Optional[str] = None,
    language: Optional[str] = None,
    context_metadata: Optional[dict] = None,
):
    payload = {
        "title": title,
        "language": language,
        "context_metadata": context_metadata or {},
    }
    try:
        resp = supabase.table("conversations").insert(payload).select("*").execute()
        if resp.data:
            return resp.data[0]
        raise HTTPException(status_code=500, detail="Failed to create conversation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages")
def get_messages(conversation_id: str, limit: int = 200, offset: int = 0):
    try:
        resp = (
            supabase.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resp.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/messages")
def create_message(conversation_id: str, payload: MessageCreate):
    """Insert a message for the conversation and update last_active_at."""
    try:
        row = {
            "conversation_id": conversation_id,
            "role": payload.role,
            "content": payload.content,
            "metadata": payload.metadata or {},
            "tokens": payload.tokens,
        }
        # insert message
        resp = supabase.table("messages").insert(row).select("*").execute()
        if not resp.data:
            raise HTTPException(status_code=500, detail="Failed to insert message")

        # update conversation last_active_at to now()
        try:
            supabase.table("conversations").update({"last_active_at": "now()"}).eq(
                "id", conversation_id
            ).execute()
        except Exception:
            # non-fatal if update fails
            pass

        return resp.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
