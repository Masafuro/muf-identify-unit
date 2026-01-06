import uuid
import secrets
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from muf import MUFClient

from .config import UNIT_NAME, REDIS_HOST, SESSION_TTL, REDIRECT_URL
from .database import r, db_session

app = FastAPI()
templates = Jinja2Templates(directory="identify-unit/templates")

@app.get("/")
async def index():
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    query = "SELECT password, user_id FROM users WHERE username = %s"
    row = db_session.execute(query, [username]).one()
    
    if not row or row.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = secrets.token_urlsafe(32)
    r.setex(f"session:{session_id}", SESSION_TTL, username)

    # MUFネットワークへの構造化データ送信
    session_payload = {
        "username": username,
        "user_id": str(row.user_id),
        "login_at": datetime.now().isoformat()
    }
    
    try:
        async with MUFClient(unit_name=UNIT_NAME, host=REDIS_HOST) as client:
            await client.send(
                status="keep",
                message_id=session_id,
                data=json.dumps(session_payload).encode('utf-8')
            )
    except Exception as e:
        print(f"MUF Network Notification Failed: {e}")

    redirect_res = RedirectResponse(url=REDIRECT_URL, status_code=303)
    redirect_res.set_cookie(
        key="session_id", value=session_id, max_age=SESSION_TTL,
        httponly=True, secure=False, samesite="lax"
    )
    return redirect_res

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    user_id = uuid.uuid4()
    query = "INSERT INTO users (username, password, user_id) VALUES (%s, %s, %s)"
    db_session.execute(query, [username, password, user_id])
    return RedirectResponse(url="/login", status_code=303)