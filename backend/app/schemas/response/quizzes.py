from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

class QuizResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    is_ai_generated: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: int
    question_type: Optional[str] = 'mcq'
    question: Optional[str] = None
    options: Optional[Any] = None
    answer: Optional[Any] = None
    is_ai_generated: Optional[bool] = None

    class Config:
        from_attributes = True


class QuizViewResponse(QuizResponse):
    questions: Optional[list[QuestionResponse]] = None

    class Config:
        from_attributes = True