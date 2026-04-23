from fastapi import APIRouter, UploadFile, File
import shutil
import os
from services.openai_service import *

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

VECTOR_STORE_ID = create_vector_store()


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_id = upload_file(file_path)

    attach_file_to_store(file_id, VECTOR_STORE_ID)

    wait_until_ready(file_id, VECTOR_STORE_ID)

    return {
        "message": "File uploaded and indexed",
        "file_id": file_id,
        "vector_store_id": VECTOR_STORE_ID
    }