import os
from dotenv import load_dotenv

load_dotenv()

# システム基本設定
UNIT_NAME = "muf-identify-unit"
SESSION_TTL = int(os.getenv("SESSION_TTL", 3600))
REDIRECT_URL = os.getenv("LOGIN_REDIRECT_URL", "/")

# データベース接続設定
REDIS_HOST = os.getenv("REDIS_HOST", "muf-redis")
SCYLLA_HOST = os.getenv("SCYLLA_HOST", "muf-scylla")
SCYLLA_KEYSPACE = os.getenv("SCYLLA_KEYSPACE", "muf_auth")