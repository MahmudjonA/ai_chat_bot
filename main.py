from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # 👈 ДОБАВЬ

from routers import upload, chat

app = FastAPI(title="AI FAQ Backend")

# 🔥 CORS НАСТРОЙКА (ВОТ СЮДА ДОБАВЛЯЕТСЯ)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # пока открываем для всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}