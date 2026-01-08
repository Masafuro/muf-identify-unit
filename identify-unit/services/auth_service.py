# identify-unit/services/auth_service.py

import json
import secrets
from datetime import datetime
from fastapi.responses import RedirectResponse
from muf import MUFClient
from ..config import UNIT_NAME, REDIS_HOST, SESSION_TTL, REDIRECT_URL, COOKIE_SECURE
from ..database import r

async def complete_auth(username: str, user_id: str):
    # 本セッションIDの生成とRedisへの保存
    session_id = secrets.token_urlsafe(32)
    r.setex(f"session:{session_id}", SESSION_TTL, username)
    
    # MUFネットワークへ送信するペイロードの準備
    session_payload = {
        "username": username,
        "user_id": user_id,
        "login_at": datetime.now().isoformat()
    }
    
    # MUFネットワークへの構造化データ送信
    try:
        async with MUFClient(unit_name=UNIT_NAME, host=REDIS_HOST) as client:
            await client.send(
                status="keep", 
                message_id=session_id, 
                data=json.dumps(session_payload).encode('utf-8')
            )
    except Exception as e:
        print(f"MUF Network Notification Failed: {e}")
    
    # 最終的なリダイレクトレスポンスの生成
    res = RedirectResponse(url=REDIRECT_URL, status_code=303)
    
    # 本セッションCookieの設定。secure属性に環境変数を適用しています。
    res.set_cookie(
        key="session_id", 
        value=session_id, 
        max_age=SESSION_TTL, 
        httponly=True, 
        secure=COOKIE_SECURE, 
        samesite="lax"
    )
    
    # 認証が完了したため、2FAプロセス用の仮Cookieを削除
    res.delete_cookie("temp_user")
    
    return res