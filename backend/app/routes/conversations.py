"""Conversation routes for single-user chatbot.

Endpoints:
- GET /conversations
- POST /conversations
- GET /conversations/{conversation_id}/messages
"""

import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder as json_encoder

from ..db import supabase
from ..models.conversations import ConversationOut, MessageOut
from ..models.prompt import PromptCreate, PromptOut
from ..routes.rag_ask import rag_ask

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/create")
def create_conversation(title: str):
    """Create a new conversation."""
    new_id = str(uuid.uuid4())
    (
        supabase.table("conversations")
        .insert({
            "id": new_id,
            "title": title,
            "created_at": "now()",
            "last_active_at": "now()",
        })
        .execute()
    )
    return {"conversation_id": new_id}


@router.get("/list", response_model=List[ConversationOut])
def get_conversations(conversation_id: str):
    resp = (
        supabase.table("conversations")
        .select("*")
        .order("last_active_at", desc=True)
        .execute()
    )

    return [
        ConversationOut(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
            last_active_at=row["last_active_at"],
        )
        for row in resp.data
    ]


@router.post("/{conversation_id}/messages/send")
def send_message(conversation_id: str, payload: PromptCreate) -> PromptOut:
    """Send a message to the chatbot."""

    # RAG call
    rag_response = rag_ask(payload)
    
    if rag_response.answer == "":
        raise HTTPException(status_code=400, detail="RAG pipeline failed to produce an answer.")

    message_id = str(uuid.uuid4())

    # Insert message
    supabase.table("messages").insert({
        "id": message_id,
        "conversation_id": conversation_id,
        "prompt": payload.query,
        "answer": rag_response.answer,
        "context_chunks": json_encoder(rag_response.sources),  # list of dicts
        "created_at": "now()",
    }).execute()

    # Update last_active_at
    supabase.table("conversations").update({"last_active_at": "now()"}).eq(
        "id", conversation_id
    ).execute()

    return rag_response


@router.get("/{conversation_id}/messages/list", response_model=List[MessageOut])
def get_messages(conversation_id: str, limit: int = 50):
    resp = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .limit(limit)
        .execute()
    )

    return [
        MessageOut(
            id=row["id"],
            prompt=row["prompt"],
            answer=row["answer"],
            context_chunks=row.get("context_chunks"),
            created_at=row["created_at"],
        )
        for row in resp.data
    ]
