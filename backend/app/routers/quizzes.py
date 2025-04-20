import os
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy import select
from pathlib import Path
from sqlalchemy import func, select, insert
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Category, QuizQuestion, User, category_note_association_table
from app.schemas.response.base import BaseResponse, ListResponse
from app.schemas.response.notes import NoteResponse
from app.schemas.request.notes import CreateNote
from app.services import CategoryService, NoteService, QuizService
from app.utils.create_note_and_quiz_ai import create_quiz as create_quiz_ai
from app.utils import logger, upload_file
from app.schemas.response.quizzes import QuizResponse, QuizViewResponse

router = APIRouter()


@router.post("/create", response_model=BaseResponse[None])
def create_quiz(
    quiz_service: Annotated[QuizService, Depends()],
    files: list[UploadFile] = File([]),
    user_prompt_input: str = Form(...),
    rag_enabled: bool = Form(False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BaseResponse[None]:
    """
    Create a quiz from a file.
    """
    try:
        saved_files = []
        if files:
            rag_enabled = True
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)

            for file in files:
                uploaded_file_path = upload_file(file)
                print("UPLOADED FILE PATH: ", uploaded_file_path)
                # file_path = upload_dir / file.filename
                # with open(file_path, "wb") as buffer:
                #     buffer.write(file.read())
                # saved_files.append(str(file_path))
                from app.utils.data_ingestor import RAG
                RAG().ingest_file(str(uploaded_file_path))

        created_quiz = create_quiz_ai(
            user_prompt_input=user_prompt_input,
            rag_enabled=rag_enabled
        )
        logger.info("Quiz created successfully.")
        title = created_quiz.get("title", "AI Generated Quiz")
        quiz_content = created_quiz.get("quiz_content", {})
        questions = quiz_content.get("questions", [])
        data = []

        db_quiz = quiz_service.create(
            {
                "title": title,
                "content": created_quiz.get("content", ""),
                "is_ai_generated": True,
                "creator_id": user.id,
            }
        )
        for question in questions:
            data.append(
                {
                    "question_type": "mcq",
                    "question": question.get("question"),
                    "options": question.get("options", []),
                    "answer": question.get("answer", ""),
                    "quiz_id": db_quiz.id,
                    "creator_id": user.id,
                    'is_ai_generated': True
                }
            )

        for question_data in data:
            db.execute(
                insert(QuizQuestion).values(**question_data)
            )
        db.commit()

        return BaseResponse(data=None, message="Quiz created successfully.")
    except Exception as e:
        logger.error(f"Error creating quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the quiz: {str(e)}",
        )


@router.get("/list", response_model=ListResponse[QuizResponse])
def list_quizzes(
    quiz_service: Annotated[QuizService, Depends()],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ListResponse[QuizResponse]:
    """
    List all quizzes created by the user.
    """
    try:
        quizzes = quiz_service.list({"creator_id": user.id})
        return ListResponse[QuizResponse](
            data=quizzes
        )
    except Exception as e:
        logger.error(f"Error retrieving quizzes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving quizzes: {str(e)}",
        )


@router.get("/{quiz_id}/view", response_model=BaseResponse[QuizViewResponse])
def view_quiz(
    quiz_service: Annotated[QuizService, Depends()],
    quiz_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BaseResponse[QuizViewResponse]:
    """
    View a specific quiz by ID.
    """
    try:
        quiz = quiz_service.get_one({"id": quiz_id, "creator_id": user.id})
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found",
            )
        return BaseResponse[QuizViewResponse](
            data=quiz
        )
    except Exception as e:
        logger.error(f"Error retrieving quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the quiz: {str(e)}",
        )
