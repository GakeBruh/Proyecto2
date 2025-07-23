import os
import secrets
import hashlib
import base64
import jwt
from datetime import datetime, timedelta, date
from fastapi import HTTPException
from dotenv import load_dotenv
from jwt import PyJWKError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def create_jwt_token(
        firstname: str,
        lastname: str,
        date_birth: date,
        email: str,
        active: bool,
        admin: bool
):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {
            "firstname": firstname,
            "lastname": lastname,
            "date_birth": str(date_birth),
            "email": email,
            "active": active,
            "admin": admin,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    return token
