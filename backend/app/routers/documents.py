from typing import Annotated
from fastapi import APIRouter, Depends, status
from app.dependencies import get_current_user
from app.models import User
from app.schemas.response import BaseResponse

router = APIRouter()

@router.get("/profile", response_model=BaseResponse[dict], status_code=status.HTTP_200_OK)
def get_profile(
    user: Annotated[User, Depends(get_current_user)],
) -> BaseResponse[dict]:
    """
    Get the profile of the current user.
    """
    return BaseResponse[dict](
        status_code=status.HTTP_200_OK,
        success=True,
        message="Profile retrieved successfully",
        data=user.to_dict(),
    )
