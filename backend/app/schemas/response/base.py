from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel

DataType = TypeVar("DataType", bound=BaseModel)

class BaseResponse(BaseModel, Generic[DataType]):
    """
    Base response model for all responses.
    """
    status_code: Optional[int] = 200
    success: Optional[bool] = True
    message: Optional[str] = None
    data: Optional[DataType] = None

    class Config:
        from_attributes = True


class ListResponse(BaseResponse[DataType]):
    """
    Base response model for list responses.
    """
    data: Optional[List[DataType]] = None

    class Config:
        from_attributes = True