from fastapi import APIRouter
from pydantic import BaseModel
from services.openai_service import ask_question

router = APIRouter()


# 📦 request schema
class Question(BaseModel):
    question: str


# 🌍 endpoint с выбором языка
@router.post("/ask/{lang}")
async def ask_with_lang(lang: str, q: Question):
    answer = ask_question(q.question, lang)

    return {
        "question": q.question,
        "answer": answer,
        "lang": lang
    }


# 🧪 дополнительный простой endpoint (без языка)
@router.post("/ask")
async def ask(q: Question):
    answer = ask_question(q.question)

    return {
        "question": q.question,
        "answer": answer,
        "lang": "default"
    }