from fastapi import APIRouter
from pydantic import BaseModel
from services.openai_service import *

router = APIRouter()


class Question(BaseModel):
    question: str


@router.post("/ask/{lang}")
async def ask_with_lang(lang: str, q: Question):
    answer = ask_question(q.question, VECTOR_STORE_ID, lang)

    return {
        "question": q.question,
        "answer": answer,
        "lang": lang
    }