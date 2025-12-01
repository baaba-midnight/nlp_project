"""
File: user.py
Project: routes
File Created: Thursday, 27th November 2025 4:34:20 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: User routes: signup, login (via Supabase), and fetch conversations.
-----
Last Modified: Thursday, 27th November 2025 7:16:01 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from typing import List
from pydantic import BaseModel

from ..models.user import UserCreate, UserLogin
from ..models.conversations import ConversationOut
from ..db import supabase


class TokenPayload(BaseModel):
    access_token: str


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


def login(payload: UserLogin):
    """Sign in a user (returns session/token)."""
    res = supabase.auth.sign_in({"email": payload.email, "password": payload.password})
    return {"status": "ok", "data": res}


def get_conversations(user_id: str):
    """Return conversations for a given user id."""
    resp = (
        supabase.table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("last_active_at", desc=True)
        .execute()
    )
    if resp.data is None:
        return []
    return resp.data
