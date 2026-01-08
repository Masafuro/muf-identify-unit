import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

# 分割した新しいルーターをインポート
# totp を totp_setup と totp_verify に置き換えます
from .routers import register, login, totp_setup, totp_verify

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 環境変数が未定義の場合はKeyErrorでプロセスを終了させる
    port = os.environ["APP_PORT"]
    print("========================================")
    print("Application is starting up...")
    print(f"Server started at http://localhost:{port}")
    print("========================================")
    yield
    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)

# それぞれのルーターを登録
app.include_router(register.router)
app.include_router(login.router)
app.include_router(totp_setup.router)
app.include_router(totp_verify.router)

@app.get("/")
async def index():
    return RedirectResponse(url="/login", status_code=303)