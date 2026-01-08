import pyotp
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..database import db_session
from ..services.auth_service import complete_auth

router = APIRouter(prefix="/totp")
templates = Jinja2Templates(directory="identify-unit/templates")

@router.get("/verify")
async def verify_page(request: Request):
    if not request.cookies.get("temp_user"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("verify_2fa.html", {"request": request})

@router.post("/verify")
async def verify_totp(request: Request, code: str = Form(...)):
    username = request.cookies.get("temp_user")
    if not username:
        raise HTTPException(status_code=401, detail="Session expired")
    
    row = db_session.execute("SELECT user_id, totp_secret FROM users WHERE username = %s", [username]).one()
    if not row or not row.totp_secret or not pyotp.TOTP(row.totp_secret).verify(code):
        raise HTTPException(status_code=401, detail="Invalid OTP")

    return await complete_auth(username, str(row.user_id))