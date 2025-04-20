from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Annotated
from fastapi import Depends
from sqlalchemy import and_, select, update as sqlalchemy_update
from sqlalchemy.orm import DeclarativeMeta, Session
from sqlalchemy.sql import Select

from app.dependencies.db import get_db
from app.models import Category, Collection, Note, Quiz, QuizQuestion, User

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseService(Generic[ModelType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def create(self, obj_in: dict) -> ModelType:
        """Instantiate and persist a new model instance."""
        try:
            db_obj = self.model(**obj_in)  # noqa: E712
            self.session.add(db_obj)
            self.session.flush()
            return db_obj
        except Exception as e:
            print(f"Error creating {self.model.__name__}: {e}")
            raise e

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key, if not soft‑deleted."""
        query: Select = select(self.model).where(
            self.model.id == id,
            self.model.is_deleted == False,  # noqa: E712
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_one(self, filters: Dict[str, Any]) -> Optional[ModelType]:
        """
        Fetch a single record matching the given filters,
        excluding any soft‑deleted rows (is_deleted == True).
        """
        conditions = [
            getattr(self.model, field) == value
            for field, value in filters.items()
            if hasattr(self.model, field)
        ]
        conditions.append(self.model.is_deleted == False)  # noqa: E712
        query: Select = select(self.model).where(and_(*conditions))

        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def list(
        self, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        List non‑deleted records matching the given filters,
        with pagination via skip/limit.
        """
        conditions = [
            getattr(self.model, field) == value
            for field, value in filters.items()
            if hasattr(self.model, field)
        ]
        conditions.append(self.model.is_deleted == False)  # noqa: E712
        combined = and_(*conditions)
        query: Select = select(self.model).where(combined).order_by(self.model.id.desc()).offset(skip).limit(limit)

        result = self.session.execute(query)
        return result.scalars().all()

    def update(self, id: Any, obj_in: dict) -> Optional[ModelType]:
        """Apply partial updates to an existing record."""
        stmt = (
            sqlalchemy_update(self.model)
            .where(self.model.id == id, self.model.is_deleted == False)  # noqa: E712
            .values(**obj_in)
            .execution_options(synchronize_session="fetch")
        )
        self.session.execute(stmt)
        self.session.flush()
        return self.get_by_id(id)

    def delete(self, id: Any) -> bool:
        """
        Soft‑delete a record by setting its `is_deleted` flag.
        Returns True if a record was marked deleted.
        """
        stmt = (
            sqlalchemy_update(self.model)
            .where(self.model.id == id, self.model.is_deleted == False)  # noqa: E712
            .values(is_deleted=True)  # type: ignore
            .execution_options(synchronize_session="fetch")
        )
        result = self.session.execute(stmt)
        self.session.flush()
        return result.rowcount > 0


class UserService(BaseService[User]):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a single user by email."""
        query = select(self.model).where(
            self.model.email == email,
            self.model.is_deleted == False,  # noqa: E712
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()


class NoteService(BaseService[Note]):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session, Note)


class CategoryService(BaseService[Category]):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session, Category)
    
    def get_or_ai_create(self, name: str, user_id: int) -> Category:
        """
        Check if a category exists by name.
        If not, create it and return the new instance.
        """
        existing_category = self.get_one({"name": name, "creator_id": user_id})
        if existing_category:
            return existing_category
        return self.create({'name': name, 'creator_id': user_id, 'is_ai_generated': True})


class CollectionService(BaseService[Collection]):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session, Collection)


class QuizService(BaseService[Quiz]):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session, Quiz)

class QuizQuestionService(BaseService[QuizQuestion]):
    def __init__(self, session: Session = Depends(get_db)):
        super().__init__(session, QuizQuestion)

