from fastapi import APIRouter, UploadFile, File
import shutil
import os

from services.openai_service import (
    upload_file,
    attach_file_to_store,
    wait_until_ready,
)

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # загружаем в OpenAI
    file_id = upload_file(file_path)

    # прикрепляем к vector store
    attach_file_to_store(file_id)

    # ждём индексацию
    wait_until_ready(file_id)

    return {
        "message": "File uploaded and indexed ✅",
        "file_id": file_id,
    }