# identify-unit/routers/register.py

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import uuid
from passlib.context import CryptContext
from ..database import db_session

router = APIRouter()
templates = Jinja2Templates(directory="identify-unit/templates")

# パスワードハッシュ化のためのコンテキスト設定
# bcryptアルゴリズムを使用します
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    user_id = uuid.uuid4()
    
    # パスワードをハッシュ化
    hashed_password = pwd_context.hash(password)
    
    # ハッシュ化されたパスワードをデータベースに保存
    query = "INSERT INTO users (username, password, user_id) VALUES (%s, %s, %s)"
    db_session.execute(query, [username, hashed_password, user_id])
    
    return RedirectResponse(url="/login", status_code=303)