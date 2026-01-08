import io
import base64
import pyotp
import qrcode
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from ..database import db_session
from ..config import UNIT_NAME
from ..services.auth_service import complete_auth

router = APIRouter(prefix="/totp")
templates = Jinja2Templates(directory="identify-unit/templates")

@router.get("/setup")
async def setup_page(request: Request):
    username = request.cookies.get("temp_user")
    if not username:
        return RedirectResponse(url="/login")
    
    secret = pyotp.random_base32()
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=UNIT_NAME)
    
    img = qrcode.make(totp_uri)
    buf = io.BytesIO()
    img.save(buf)
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    
    return templates.TemplateResponse("setup_2fa.html", {
        "request": request, "qr_b64": qr_b64, "secret": secret
    })

@router.post("/setup")
async def setup_verify(request: Request, secret: str = Form(...), code: str = Form(...)):
    username = request.cookies.get("temp_user")
    if not username:
        raise HTTPException(status_code=401, detail="Session expired")

    if not pyotp.TOTP(secret).verify(code):
        raise HTTPException(status_code=401, detail="Invalid verification code.")

    query = "SELECT user_id FROM users WHERE username = %s"
    row = db_session.execute(query, [username]).one()
    db_session.execute("UPDATE users SET totp_secret = %s WHERE username = %s", [secret, username])

    return await complete_auth(username, str(row.user_id))