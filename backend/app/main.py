"""
File: main.py
Project: app
File Created: Sunday, 16th November 2025 1:14:16 AM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Sunday, 16th November 2025 1:15:46 AM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router()
