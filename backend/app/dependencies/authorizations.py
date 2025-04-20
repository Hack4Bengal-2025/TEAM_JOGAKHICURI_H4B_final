from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils import JWTManager
from typing import Annotated, Optional
from app.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin")


def get_current_user(
    # token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends()],
):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )

    # payload = JWTManager.verify_access_token(token, credentials_exception)
    # if payload is None:
    #     raise credentials_exception
    
    # user_id: Optional[str] = payload.get("sub") if payload else None
    # if not user_id:
    #     raise credentials_exception

    user = user_service.get_by_id(1)

    # if user is None:
    #     raise credentials_exception

    return user
