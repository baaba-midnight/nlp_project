"""Conversation routes for single-user chatbot.

Endpoints:
- GET /conversations
- POST /conversations
- GET /conversations/{conversation_id}/messages
"""

from typing import Optional, List

from fastapi import APIRouter

from ..db import supabase
from ..models.conversations import MessageCreate, ConversationOut

# Use router prefix so paths are concise and unique
router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", summary="List conversations")
def list_conversations(limit: int = 50, offset: int = 0) -> List[ConversationOut]:
    resp = (
        supabase.table("conversations")
        .select("*")
        .order("last_active_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    conversations = []

    for r in resp.data:
        conversations.append(ConversationOut(r))

    return conversations


@router.post("", summary="Create a conversation")
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
    resp = supabase.table("conversations").insert(payload).select("*").execute()
    if resp.data:
        return resp.data[0]
    raise RuntimeError("Failed to create conversation")


@router.get("/{conversation_id}/messages", summary="Get messages for a conversation")
def get_messages(conversation_id: str, limit: int = 200, offset: int = 0):
    resp = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return resp.data or []


@router.post(
    "/{conversation_id}/messages", summary="Create a message in a conversation"
)
def create_message(conversation_id: str, payload: MessageCreate):
    row = {
        "conversation_id": conversation_id,
        "role": payload.role,
        "content": payload.content,
        "metadata": payload.metadata or {},
        "tokens": payload.tokens,
    }

    resp = supabase.table("messages").insert(row).select("*").execute()

    if not resp.data:
        raise RuntimeError("Failed to insert message")

    supabase.rpc("update_last_active", {"cid": conversation_id}).execute()

    return resp.data[0]
