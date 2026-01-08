# identify-unit/routers/login.py

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from ..database import db_session
from ..config import COOKIE_SECURE  # 設定値のインポートを追加

router = APIRouter()
templates = Jinja2Templates(directory="identify-unit/templates")

# パスワードハッシュ化・検証用コンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # データベースからハッシュ化されたパスワードと2FA秘密鍵の有無を取得
    query = "SELECT password, totp_secret FROM users WHERE username = %s"
    row = db_session.execute(query, [username]).one()
    
    # ユーザーが存在しない、またはハッシュ値が一致しない場合の処理
    if not row or not pwd_context.verify(password, row.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # パスワード認証成功後の2FA分岐ロジック
    if not row.totp_secret:
        # 2FA未設定なら設定画面へ
        response = RedirectResponse(url="/totp/setup", status_code=303)
    else:
        # 2FA設定済みなら検証画面へ
        response = RedirectResponse(url="/totp/verify", status_code=303)
    
    # 2FAプロセス中にユーザーを特定するための一時的なCookieをセット（有効期限5分）
    # secure属性を環境変数から取得した設定値に変更しました
    response.set_cookie(
        key="temp_user", 
        value=username, 
        httponly=True, 
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=300
    )
    return response