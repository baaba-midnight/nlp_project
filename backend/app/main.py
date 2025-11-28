"""
File: main.py
Project: app
File Created: Sunday, 16th November 2025 1:14:16 AM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: FastAPI application entrypoint and router registration.
-----
Last Modified: Friday, 28th November 2025 11:09:51 AM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import conversations, rag_ask, upload

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG ask endpoint (mounted under /api -> results in /api/rag/ask)
app.include_router(rag_ask.router, prefix="/api")

# Upload endpoint(s) under /api (e.g. POST /api/upload)
app.include_router(upload.router, prefix="/api")

# Conversations router has its own prefix (/conversations)
app.include_router(conversations.router)
