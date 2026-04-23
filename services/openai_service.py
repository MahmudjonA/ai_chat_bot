from openai import OpenAI
import os
from dotenv import load_dotenv
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ✅ Берём store из .env
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")


# ---------- CREATE STORE (только если нет) ----------
def create_vector_store(name="faq_store"):
    vs = client.vector_stores.create(name=name)
    return vs.id


# ---------- FILE UPLOAD ----------
def upload_file(file_path):
    with open(file_path, "rb") as f:
        file = client.files.create(
            file=f,
            purpose="assistants"
        )
    return file.id


def attach_file_to_store(file_id):
    client.vector_stores.files.create(
        vector_store_id=VECTOR_STORE_ID,
        file_id=file_id
    )


# ---------- WAIT ----------
def wait_until_ready(file_id):
    while True:
        status = client.vector_stores.files.retrieve(
            vector_store_id=VECTOR_STORE_ID,
            file_id=file_id
        )

        if status.status == "completed":
            return True
        time.sleep(2)


# ---------- LANGUAGE ----------
def get_instructions(lang: str):
    if lang == "ru":
        return """
        Ты ассистент по документам.

        Правила:
        - отвечай только по документам
        - если нет ответа — скажи "не найдено"
        - не выдумывай

        Формат:
        - коротко
        - просто
        - только суть
        """

    elif lang == "en":
        return """
        Answer only using the documents.
        If not found — say "not found".
        Keep it short and simple.
        """

    elif lang == "uz":
        return """
        Faqat hujjatlar asosida javob ber.
        Agar bo‘lmasa — "topilmadi".
        Qisqa va oddiy yoz.
        """

    return "Answer simply."


# ---------- ASK ----------
def ask_question(question, lang="ru"):
    instructions = get_instructions(lang)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID],
        }],
        instructions=instructions
    )

    return response.output_text
    
def get_or_create_vector_store():
    store_id = os.getenv("VECTOR_STORE_ID")

    # если уже есть — используем
    if store_id:
        return store_id

    # если нет — создаём новый
    vs = client.vector_stores.create(name="faq_store")

    print("🔥 NEW VECTOR STORE CREATED:", vs.id)
    print("👉 ADD THIS TO .env:")
    print(f"VECTOR_STORE_ID={vs.id}")

    return vs.id