# identify-unit/config.py

import os
from dotenv import load_dotenv

load_dotenv()

UNIT_NAME = "identify-unit"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
SCYLLA_HOST = os.getenv("SCYLLA_HOST", "localhost")
SCYLLA_KEYSPACE = os.getenv("SCYLLA_KEYSPACE", "muf_auth")

SESSION_TTL = int(os.getenv("SESSION_TTL", 3600))
REDIRECT_URL = os.getenv("LOGIN_REDIRECT_URL")

# 文字列の"true"をブール値のTrueに変換
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"