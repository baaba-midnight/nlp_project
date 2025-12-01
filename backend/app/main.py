"""
File: main.py
Project: app
File Created: Sunday, 16th November 2025 1:14:16 AM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: Compatibility layer: expose previously-defined route handlers as plain functions
so they can be imported and used directly from Streamlit or other non-HTTP callers.

This module no longer instantiates a FastAPI `app` — it simply re-exports
functions from the former route modules.
-----
Last Modified: Monday, 1st December 2025 1:32:27 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from .routes import conversations, rag_ask, upload

# Conversations
list_conversations = conversations.list_conversations
create_conversation = conversations.create_conversation
get_messages = conversations.get_messages
create_message = conversations.create_message

# RAG
rag_ask = rag_ask.rag_ask

# Uploads
process_uploads = upload.process_uploads
