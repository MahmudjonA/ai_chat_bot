from fastapi import FastAPI
from routers import upload, chat

app = FastAPI(title="AI FAQ Backend")

app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}