"""
File: user.py
Project: models
File Created: Thursday, 27th November 2025 4:34:41 PM
Author: baaba-midnight
Email: baaba.amosah@gmail.com
Version: 1.0
Brief: <<brief>>
-----
Last Modified: Thursday, 27th November 2025 7:14:35 PM
Modified By: baaba-midnight
-----
Copyright ©2025 baaba-midnight
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
