from typing import Any, Optional
from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

import pytz
from app.config import config
from passlib.context import CryptContext
import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession

class PasswordManager:
    @classmethod
    def hash_password(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class JWTManager:
    @staticmethod
    def encode_data(data: dict, expires_delta: timedelta = None) -> str:
        """
        Create a JWT token with an expiration time.
        """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(seconds=config.JWT_ACCESS_TOKEN_EXPIRES)
        )
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str, credentials_exception) -> Optional[dict[str, Any]]:
        """
        Verify the JWT token and extract the sub from it.
        """
        try:
            payload = jwt.decode(
                token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
            )
            
            sub, type = payload.get("sub"), payload.get("type")
            if type is None or sub is None:
                raise credentials_exception
            
            if type != "access":
                raise credentials_exception
            
            return {"sub": sub}
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    def verify_refresh_token(token: str, credentials_exception) -> Optional[dict[str, Any]]:
        """
        Verify the JWT token and extract the sub from it.
        """
        try:
            payload = jwt.decode(
                token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
            )
            
            sub, type = payload.get("sub"), payload.get("type")
            if type is None or sub is None:
                raise credentials_exception
            
            if type != "refresh":
                raise credentials_exception
            
            token_data = {"sub": sub}
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict[str, Any]]:
        """
        Decode the JWT token and return the payload.
        """
        try:
            payload = jwt.decode(
                token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None