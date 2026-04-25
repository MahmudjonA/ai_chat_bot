from openai import OpenAI
import os
from dotenv import load_dotenv
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 🔥 cache (чтобы не создавать каждый раз)
VECTOR_STORE_ID = None


# ---------- GET OR CREATE VECTOR STORE ----------
def get_or_create_vector_store():
    global VECTOR_STORE_ID

    # 1. если уже есть в памяти
    if VECTOR_STORE_ID:
        return VECTOR_STORE_ID

    # 2. если есть в env
    env_id = os.getenv("VECTOR_STORE_ID")
    if env_id:
        VECTOR_STORE_ID = env_id
        print("✅ Using VECTOR_STORE_ID from ENV:", VECTOR_STORE_ID)
        return VECTOR_STORE_ID

    # 3. пробуем найти существующий
    stores = client.vector_stores.list()

    for store in stores.data:
        if store.name == "faq_store":
            VECTOR_STORE_ID = store.id
            print("✅ Found existing store:", VECTOR_STORE_ID)
            return VECTOR_STORE_ID

    # 4. если нет — создаём
    vs = client.vector_stores.create(name="faq_store")
    VECTOR_STORE_ID = vs.id

    print("🔥 Created NEW vector store:", VECTOR_STORE_ID)

    return VECTOR_STORE_ID


# ---------- FILE UPLOAD ----------
def upload_file(file_path):
    with open(file_path, "rb") as f:
        file = client.files.create(
            file=f,
            purpose="assistants"
        )
    return file.id


def attach_file_to_store(file_id):
    vs_id = get_or_create_vector_store()

    client.vector_stores.files.create(
        vector_store_id=vs_id,
        file_id=file_id
    )


# ---------- WAIT ----------
def wait_until_ready(file_id):
    vs_id = get_or_create_vector_store()

    while True:
        status = client.vector_stores.files.retrieve(
            vector_store_id=vs_id,
            file_id=file_id
        )

        if status.status == "completed":
            return True

        print("⌛ Processing file...")
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
        Qisqa va oddiy yoz!
        """

    return "Answer simply."


# ---------- ASK ----------
def ask_question(question, lang="ru"):
    vs_id = get_or_create_vector_store()

    instructions = get_instructions(lang)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vs_id],
        }],
        instructions=instructions
    )

    return response.output_text