from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, model_validator

class CategoryResponse(BaseModel):
    id: int
    name: str
    is_ai_generated: Optional[bool] = False
    
    class Config:
        from_attributes = True

class CollectionResponse(CategoryResponse):
    pass


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    is_ai_generated: Optional[bool] = False
    categories: Optional[List[CategoryResponse]] = []
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True