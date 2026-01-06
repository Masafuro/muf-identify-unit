import time
import redis
from cassandra.cluster import Cluster
from .config import REDIS_HOST, SCYLLA_HOST, SCYLLA_KEYSPACE

# Redisクライアントの初期化
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# ScyllaDBセッションの取得（リトライロジック付き）
def get_db_session():
    retries = 10
    while retries > 0:
        try:
            cluster = Cluster([SCYLLA_HOST])
            session = cluster.connect()
            session.execute(
                f"CREATE KEYSPACE IF NOT EXISTS {SCYLLA_KEYSPACE} "
                "WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
            )
            session.set_keyspace(SCYLLA_KEYSPACE)
            session.execute(
                "CREATE TABLE IF NOT EXISTS users ("
                "username text PRIMARY KEY, password text, user_id uuid)"
            )
            return session
        except Exception as e:
            print(f"ScyllaDB connection failed (retrying in 5s...): {e}")
            retries -= 1
            time.sleep(5)
    raise Exception("ScyllaDB connection failed after retries.")

db_session = get_db_session()