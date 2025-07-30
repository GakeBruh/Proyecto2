import os
import secrets
import hashlib
import base64
import jwt

from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()


def create_jwt_token(
        firstname:str
        , lastname:str
        , email: str
        , active: bool
        , admin: bool
        , id: str
):
    expiration = datetime.utcnow() + timedelta(hours=1)  # El token expira en 1 hora
    token = jwt.encode(
        {
            "id": id,
            "firstname": firstname,
            "lastname": lastname,
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

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        email = payload.get("email")
        firstname = payload.get("firstname")
        lastname = payload.get("lastname")
        active = payload.get("active")
        admin = payload.get("admin", False)
        exp = payload.get("exp")
        user_id = payload.get("id")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Token Invalid")
        
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")
        
        if not active:
            raise HTTPException(status_code=401, detail="Inactive user")
        
        return {
            "id": user_id,
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "active": active,
            "role": "admin" if admin else "user"
        }
        
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")


def validate_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        email = payload.get("email")
        firstname = payload.get("firstname")
        lastname = payload.get("lastname")
        active = payload.get("active")
        admin = payload.get("admin", False)
        exp = payload.get("exp")
        user_id = payload.get("id")
        
        if email is None:
            raise HTTPException(status_code=401, detail="Token Invalid")
        
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Expired token")
        
        if not active or not admin:
            raise HTTPException(status_code=401, detail="Inactive user or not admin")
        
        return {
            "id": user_id,
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "active": active,
            "role": "admin"
        }
        
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")