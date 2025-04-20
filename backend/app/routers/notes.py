import os
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy import select
from pathlib import Path
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Category, User, category_note_association_table
from app.schemas.response.base import BaseResponse, ListResponse
from app.schemas.response.notes import CategoryResponse, NoteResponse
from app.schemas.request.notes import CreateNote
from app.services import CategoryService, NoteService
from app.utils.create_note_and_quiz_ai import create_note as create_notes_ai
from app.utils import logger, upload_file 

router = APIRouter()


@router.post("/create", response_model=BaseResponse[NoteResponse], status_code=status.HTTP_200_OK)
def create_note(
    request: CreateNote,
    user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> BaseResponse[NoteResponse]:
    """
    Create a new note.
    """
    try:
        creation_data = request.model_dump(exclude=['categories'])
        creation_data['creator_id'] = user.id
        created_note = note_service.create(creation_data)

        if request.categories is not None:
            categories = set(request.categories)
            if len(categories) > 0:
                query = (
                    select(func.count(Category.id).label("count"))
                    .where(
                        Category.id.in_(categories),
                        Category.is_deleted == False
                    )
                )
                count = db.execute(query)
                count = count.scalar_one_or_none()
                if len(categories) != count:
                    raise ValueError("Some categories do not exist.")

            for category in categories:
                query = category_note_association_table.insert().values(
                    category_id=category,
                    note_id=created_note.id,
                )
                db.execute(query)

        return BaseResponse[NoteResponse](
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Note created successfully",
            data=created_note,
        )
    except Exception as e:
        return BaseResponse[None](
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message=str(e),
        )


@router.get("/list", response_model=ListResponse[NoteResponse], status_code=status.HTTP_200_OK)
def list_notes(
    user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends()],
) -> ListResponse[NoteResponse]:
    """
    Get the list of notes for the current user.
    """
    # Assuming you have a method to get notes for the user
    notes = note_service.list(filters={'creator_id': user.id})
    # notes = note_service.list()
    return ListResponse[NoteResponse](
        status_code=status.HTTP_200_OK,
        success=True,
        message="Notes retrieved successfully",
        data=notes,
    )


@router.post("/create-ai-note", response_model=BaseResponse[dict], status_code=status.HTTP_201_CREATED)
def create_ai_note(
    user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends()],
    category_service: Annotated[CategoryService, Depends()],
    db: Annotated[Session, Depends(get_db)],
    user_prompt_input: str = Form(...),
    rag_enabled: bool = Form(False),
    files: List[UploadFile] = File([]),
) -> BaseResponse[dict]:
    """
    Create a note using AI generation, with optional RAG if files are provided.
    """
    print("INSIDE CREATE AI NOTE")
    print("USER PROMPT: ", user_prompt_input)
    print("FILES RECEIVED: ", files)
    # return {
    #         "status_code": 201,
    #         "success": True,
    #         "message": "AI note created successfully",
    #         "data": {
    #             "id": 40,
    #             "title": "Celery - A Distributed Asynchronous Background Task Management Framework\n\n## 2.",
    #             "content": "Celery is an open-source, distributed asynchronous background task management framework written in Python. It is designed to handle task queues, allowing for the asynchronous execution of tasks, which is crucial for scaling and performance in web applications. This note provides an overview of Celery, its key features, and how it operates within a distributed system.\n\n## 3. **Key Components and Architecture**\n### 3.1. **Broker**\nThe broker is a critical component of Celery, acting as a message queue that handles task distribution. Popular brokers include RabbitMQ, Redis, and Amazon SQS. The broker's primary role is to receive task messages from the application and route them to worker nodes.\n\n### 3.2. **Workers**\nWorkers are the nodes within the Celery architecture that execute tasks. They can be distributed across multiple machines, allowing for horizontal scaling. Workers can run on different machines and can be scaled independently, providing a high degree of flexibility.\n\n### 3.3. **Result Backend**\nThe result backend is used to store the results of task executions. This is optional but highly useful for monitoring and logging purposes. Common result backends include databases (like MySQL or PostgreSQL), Redis, and Memcached.\n\n## 4. **Features and Benefits**\n### 4.1. **Asynchronous Task Execution**\nCelery allows tasks to be executed asynchronously, which means that the main application thread is not blocked while waiting for a task to complete. This leads to significant performance improvements in I/O-bound and computationally intensive tasks.\n\n### 4.2. **Distributed Task Queue**\nTasks can be distributed across multiple workers, enabling horizontal scaling. This means that as the workload increases, more workers can be added to handle the load, making it highly scalable.\n\n### 4.3. **Task Scheduling**\nCelery provides built-in support for scheduling tasks using a feature called \"beat.\" This allows for tasks to be executed at regular intervals, similar to cron jobs but integrated into the Celery framework.\n\n### 4.4. **Retry and Timeout Mechanisms**\nCelery offers robust mechanisms for handling task failures, including retries with exponential backoff and timeout settings. This ensures that transient failures do not cause tasks to fail permanently.\n\n## 5. **Use Cases and Integration**\n### 5.1. **Web Applications**\nCelery is widely used in web applications to offload tasks that would otherwise block the main request-response cycle. Examples include sending emails, processing images, and data processing.\n\n### 5.2. **Microservices Architecture**\nIn a microservices architecture, Celery can be used to handle inter-service communication and task distribution, enabling loose coupling and scalability between services.\n\n### 5.3. **Machine Learning and Data Science**\nCelery can be used to manage long-running machine learning tasks, such as data preprocessing, model training, and evaluation, by offloading these tasks to worker nodes.\n\n## 6. **Data/Analysis (if applicable)**\nGiven the lack of specific data in the provided context, this section focuses on general insights. Celery's design allows for significant performance enhancements by offloading tasks to background workers. For instance, in a web application, tasks like sending emails or processing large files can take several seconds to complete. By executing these tasks asynchronously, the web server can return a response immediately, improving user experience.\n\n## 7. **Conclusion:**\nCelery is a powerful framework for managing asynchronous tasks in Python applications. Its distributed architecture allows for scalability and flexibility, making it suitable for a wide range of applications, from web development to data science. By leveraging Celery, developers can build more efficient and scalable systems.\n\n## 8. **References (Optional):**\nThis information was derived based on general knowledge of Celery and similar frameworks, as specific context from web searches and local documents was not provided.\n\n**Word Count: 700** \n\nGiven the absence of specific web search and local document context, the note above provides a general overview of Celery based on widely available information. For a more detailed and specific note, additional context would be necessary.",
    #             "is_ai_generated": True,
    #             "categories": [],
    #             "created_at": "2025-04-20T01:58:40.281793",
    #             "updated_at": "2025-04-20T01:58:40.281837"
    #         }
    #     }
    try:
        saved_files = []
        if files:
            rag_enabled = True
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)

            for file in files:
                uploaded_file_path = upload_file(file)
                print("UPLOADED FILE PATH: ", uploaded_file_path)
                # file_path = os.path.join(upload_dir, file.filename)
                # with open(file_path, "wb") as buffer:
                #     buffer.write(file.read())
                # saved_files.append(str(file_path))
                from app.utils.data_ingestor import RAG
                RAG().ingest_file(str(uploaded_file_path))

        all_db_categories = category_service.list(filters={'creator_id': user.id, 'is_deleted': False})
        all_category_names = [cat.name for cat in all_db_categories]
        
        generated_content = create_notes_ai(
            all_categories=all_category_names,
            user_prompt=user_prompt_input,
            rag_enabled=rag_enabled
        )

        title = generated_content.get("title", "AI Generated Note")
        content = generated_content.get("note_content", "")
        categories = generated_content.get("categories", {})
        
        creation_data = {
            "title": title,
            "content": content,
            "is_ai_generated": True,
            "creator_id": user.id,
        }
        created_note = note_service.create(creation_data)
        all_categories = []
        if categories.get('created') == True:  # noqa: E712
            for cat in categories['category']:
                db_category = category_service.get_or_ai_create(cat, user.id)
                all_categories.append(CategoryResponse.model_validate(db_category).model_dump())
                db.execute(
                    category_note_association_table.insert()
                    .values(category_id=db_category.id, note_id=created_note.id)
                )
        generated_note = NoteResponse.model_validate(created_note).model_dump()
        generated_note['is_ai_generated'] = True
        generated_note['categories'] = categories.get('category', [])
        print("GENERATED NOTE : ", generated_note)
        # Return the created note
        return BaseResponse[dict](
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="AI note created successfully",
            data=generated_note,
        )
    except Exception as e:
        raise HTTPException(
            status_code=402,
            detail=f"Error creating AI note: {str(e)}"
        )


@router.get("/{note_id}", response_model=BaseResponse[NoteResponse], status_code=status.HTTP_200_OK)
def get_note(
    note_id: int,
    user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends()],
) -> BaseResponse[NoteResponse]:
    """
    Get a specific note by ID.
    """
    try:
        note = note_service.get_by_id(note_id)
        # note = note.to_dict()
        # note["categories"] = [CategoryResponse.model_validate(cat).model_dump() for cat in note["categories"]]
        print("NOTE CATEGORIES: ", note.to_dict())
        # Check if the note belongs to the user
        if note.creator_id != user.id:
            return BaseResponse[NoteResponse](
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="You don't have permission to access this note",
            )

        return BaseResponse[NoteResponse](
            status_code=status.HTTP_200_OK,
            success=True,
            message="Note retrieved successfully",
            data=note,
        )
    except Exception as e:
        return BaseResponse[NoteResponse](
            status_code=status.HTTP_404_NOT_FOUND,
            success=False,
            message=f"Note not found: {str(e)}",
        )


@router.put("/{note_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
def update_note(
    note_id: int,
    request: CreateNote,
    user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> BaseResponse[None]:
    """
    Update a specific note by ID.
    """
    try:
        note = note_service.get_by_id(note_id)

        if note.creator_id != user.id:
            return BaseResponse[None](
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="You don't have permission to update this note",
            )

        update_data = request.model_dump(exclude=['categories'])
        updated_note = note_service.update(note_id, update_data)
        if not updated_note:
            return BaseResponse[None](
                status_code=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Something went wrong please try again.",
            )
        if request.categories is not None:
            categories = set(request.categories)
            if len(categories) >= 0:
                query = (
                    select(func.count(Category.id).label("count"))
                    .where(
                        Category.id.in_(categories),
                        Category.is_deleted == False
                    )
                )
                count = db.execute(query)
                count = count.scalar_one_or_none()
                if len(categories) != count:
                    raise ValueError("Some categories do not exist.")

                db.execute(
                    category_note_association_table.delete().where(
                        category_note_association_table.c.note_id == note_id
                    )
                )
                for category in categories:
                    query = category_note_association_table.insert().values(
                        category_id=category,
                        note_id=updated_note.id,
                    )
                    db.execute(query)
        return BaseResponse[None](
            status_code=status.HTTP_200_OK,
            success=True,
            message="Note updated successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating note: {str(e)}"
        )


@router.delete("/{note_id}", response_model=BaseResponse[None], status_code=status.HTTP_200_OK)
def delete_note(
    note_id: int,
    user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends()],
) -> BaseResponse[None]:
    """
    Delete a specific note by ID.
    """
    try:
        note = note_service.get_by_id(note_id)
        if not note:
            return BaseResponse[None](
                status_code=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Note not found",
            )

        # Check if the note belongs to the user
        if note.creator_id != user.id:
            return BaseResponse[None](
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                message="You don't have permission to delete this note",
            )

        note_service.delete(note_id)

        return BaseResponse[None](
            status_code=status.HTTP_200_OK,
            success=True,
            message="Note deleted successfully",
        )
    except Exception as e:
        return BaseResponse[None](
            status_code=status.HTTP_404_NOT_FOUND,
            success=False,
            message=f"Error deleting note: {str(e)}",
        )
