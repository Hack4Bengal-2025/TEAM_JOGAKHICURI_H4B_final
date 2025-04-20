from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import User
from app.schemas.request import SignUpRequest, SignInRequest
from app.dependencies.db import get_db
from app.schemas.response.base import BaseResponse
from app.services import UserService
from app.utils import JWTManager

router = APIRouter()

@router.post("/signup", response_model=BaseResponse[None], status_code=status.HTTP_201_CREATED)
def signup(
    request: SignUpRequest,
    user_service: Annotated[UserService, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        existing_user = user_service.get_one({'email': request.email})
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        existing_user = user_service.get_one({'username': request.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        try:
            new_user = user_service.create(request.model_dump())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating user: " + str(e),
            ) from e
        return BaseResponse(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="User created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.post("/signin", response_model=BaseResponse[dict], status_code=status.HTTP_200_OK)
def signin(
    request: SignInRequest,
    user_service: Annotated[UserService, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        user = user_service.get_one({'email': request.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        if not user.verify_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        access_token = JWTManager.encode_data({'sub': str(user.id), 'type': 'access'}, timedelta(minutes=10))
        ref_exp = timedelta(days=7) if request.remember_me else timedelta(hours=3)
        refresh_token = JWTManager.encode_data({'sub': str(user.id), 'type': 'refresh'}, ref_exp)
        
        return BaseResponse[dict](
            data={
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred. {e}",
        )

