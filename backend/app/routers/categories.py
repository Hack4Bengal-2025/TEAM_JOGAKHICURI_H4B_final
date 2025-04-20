from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.models import User
from app.schemas.request.notes import CreateCategory
from app.schemas.response.base import BaseResponse, ListResponse
from app.schemas.response.notes import CategoryResponse
from app.services import CategoryService
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db


router = APIRouter()

@router.post("/create", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
def create_category(
    request: CreateCategory,
    user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoryService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BaseResponse[None]:
    try:
        existing_category = category_service.get_one({'name': request.name})
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists",
            )
        creation_data = request.model_dump()
        creation_data['creator_id'] = user.id
        category_service.create(creation_data)
        
        return BaseResponse[None](
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Category created successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating category: " + str(e),
        )


@router.get("/list", response_model=ListResponse[CategoryResponse], status_code=status.HTTP_200_OK)
def list_categories(
    user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoryService, Depends()],
) -> ListResponse[CategoryResponse]:
    try:
        categories = category_service.list({'creator_id': user.id})
        return ListResponse[CategoryResponse](
            status_code=status.HTTP_200_OK,
            success=True,
            message="Categories retrieved successfully",
            data=categories,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error retrieving categories: " + str(e),
        )


@router.delete("/delete/{category_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
def delete_category(
    category_id: int,
    user: Annotated[User, Depends(get_current_user)],
    category_service: Annotated[CategoryService, Depends()],
) -> BaseResponse[None]:
    try:
        category = category_service.get_one({'id': category_id, 'creator_id': user.id})
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        category_service.delete(category_id)
        return BaseResponse[None](
            status_code=status.HTTP_200_OK,
            success=True,
            message="Category deleted successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error deleting category: " + str(e),
        )