from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .categories import router as categories_router
from .notes import router as notes_router
from .collections import router as collections_router
from .quizzes import router as quizzes_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication APIs"])
router.include_router(user_router, prefix="/user", tags=["User APIs"])
router.include_router(categories_router, prefix="/categories", tags=["Category APIs"])
router.include_router(notes_router, prefix="/notes", tags=["Notes APIs"])
router.include_router(collections_router, prefix="/collections", tags=["Collections APIs"])
router.include_router(quizzes_router, prefix="/quizzes", tags=["Quiz APIs"])
