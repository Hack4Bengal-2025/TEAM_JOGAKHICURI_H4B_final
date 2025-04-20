from pydantic import BaseModel, Field
from typing import List

class Categories(BaseModel):
    """Pydantic model to represent the categorized output."""
    category: List[str] = Field(description="List of category names assigned to the prompt.")
    created: bool = Field(description="True if a new category was created, False otherwise.")

