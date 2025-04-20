from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.dependencies import get_current_user, get_db
from app.models import Category, User, category_note_association_table
from app.schemas.response.base import BaseResponse, ListResponse
from app.schemas.response.notes import CollectionResponse
from app.schemas.request.notes import CreateCollection
from app.services import CollectionService

router = APIRouter()

@router.post("/create", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
def create_collection(
    request: CreateCollection,
    collection_service: Annotated[CollectionService, Depends()],
    user: Annotated[User, Depends(get_current_user)],
):
    try:
        existing = collection_service.get_one({'name': request.name})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Collection already exists",
            )
        
        creation_data = request.model_dump()
        creation_data['creator_id'] = user.id
        
        collection_service.create(creation_data)
        
        return BaseResponse[None](
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Collection created successfully",
        )
    except Exception as e:
        return BaseResponse[None](
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Error creating collection: " + str(e),
        )

@router.get("/list", response_model=ListResponse[CollectionResponse], status_code=status.HTTP_200_OK)
def list_collections(
    user: Annotated[User, Depends(get_current_user)],
    collection_service: Annotated[CollectionService, Depends()],
) -> ListResponse[CollectionResponse]:
    try:
        collections = collection_service.list({'creator_id': user.id})
        return ListResponse[CollectionResponse](
            status_code=status.HTTP_200_OK,
            success=True,
            message="Collections retrieved successfully",
            data=collections,
        )
    except Exception as e:
        return BaseResponse[None](
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Error retrieving collections: " + str(e),
        )