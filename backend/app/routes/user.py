"""
File: user.py
Project: routes
File Created: Thursday, 27th November 2025 4:34:20 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: User routes: signup, login (via Supabase), and fetch conversations.
-----
Last Modified: Thursday, 4th December 2025 10:57:38 AM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from fastapi import APIRouter
from pydantic import BaseModel

from ..models.user import UserCreate, UserLogin
from ..models.conversations import ConversationOut
from ..db import supabase

router = APIRouter()


class TokenPayload(BaseModel):
    access_token: str


@router.post("/user/signup")
def signup(payload: UserCreate):
    """Create a user in Supabase Auth (sign up).

    If the Supabase client in this environment has the service role key, this will
    attempt an admin create; otherwise it will call the regular sign_up flow.
    """
    # try admin create_user (service role)
    admin = getattr(supabase.auth, "admin", None)
    if admin and hasattr(admin, "create_user"):
        user = admin.create_user({
            "email": payload.email,
            "password": payload.password,
            "email_confirm": True,
        })
        return {"status": "ok", "user": user}

    # fallback to public sign_up
    res = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
    return {"status": "ok", "data": res}


@router.post("/user/login")
def login(payload: UserLogin):
    """Sign in a user (returns session/token)."""
    res = supabase.auth.sign_in({"email": payload.email, "password": payload.password})
    return {"status": "ok", "data": res}


@router.get("/user/{user_id}/conversations")
def get_conversations(user_id: str):
    """Return conversations for a given user id."""
    resp = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("last_active_at", desc=True)
        .execute()
    )
    
    conversations = []
    for item in resp.data or []:
        conversations.append(ConversationOut(**item))
    return conversations
