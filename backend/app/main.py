from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import conversations, rag_ask, upload

app = FastAPI()

# CORS Middleware due to frontend and backend running on different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload.router)
app.include_router(conversations.router)
app.include_router(rag_ask.router)
