import os
from dotenv import load_dotenv
from celery import Celery
from app.config import config
load_dotenv()

celery = Celery(
    __name__,
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
)