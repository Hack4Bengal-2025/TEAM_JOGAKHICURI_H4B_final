from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime

class CreateCollection(BaseModel):
    name: str = Field(..., example="My Collection")
    is_ai_generated: Optional[bool] = Field(False)


class CreateCategory(BaseModel):
    name: str = Field(...)
    is_ai_generated: Optional[bool] = Field(False)

class CreateNote(BaseModel):
    title: str = Field(..., example="Note Title")
    content: str = Field(..., example="This is the content of the note.")
    categories: Optional[List[int]] = None
    is_ai_generated: Optional[bool] = Field(False)