from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime


class SignUpRequest(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    email: EmailStr
    username: Optional[constr(pattern=r"^[a-zA-Z0-9_]{3,50}$",)] = Field(..., example="johndoe") # type: ignore
    password: constr(min_length=8, max_length=128) = Field(..., example="password123") # type: ignore
    dob: Optional[datetime] = Field(None, example="2000-01-01")

class SignInRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128) = Field(..., example="password123") # type: ignore
    remember_me: Optional[bool] = Field(False, example=True)

