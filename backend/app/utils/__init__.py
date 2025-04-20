import os
from pathlib import Path
import shutil
from typing import Dict
import uuid
import logging

from fastapi import HTTPException, UploadFile
from app.config import config
from .security import JWTManager, PasswordManager

UPLOAD_DIR = Path(config.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger('Joga Khichuri')
logger.setLevel(logging.DEBUG)

folder_by_content_type: Dict[str, str] = {
    "image": "images",
    "application": "documents",
    # "text": "texts",
    # "audio": "audios",
}

def upload_file(file: UploadFile) -> Path:
    main_type = file.content_type.split("/")[0]
    folder_name = folder_by_content_type.get(main_type)
    
    if folder_name is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )
    
    upload_path = UPLOAD_DIR / folder_name
    upload_path.mkdir(parents=True, exist_ok=True)

    filename_uuid = f"{uuid.uuid4()}{Path(file.filename).suffix}"
    file_path = upload_path / filename_uuid
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


def remove_existing_file(existing_image_path: str):
    existing_image_path = Path("uploads/" + existing_image_path)
    if existing_image_path.exists():
        os.remove(existing_image_path)
    return