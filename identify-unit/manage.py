import sys
import argparse
from .database import db_session
# ScyllaDB 管理用スクリプト
# <コンテナID>はidentify-unitのもの
# データベース確認
# docker exec -it <コンテナID> python -m identify-unit.manage list
# 認証情報初期化
# docker exec -it <コンテナID> python -m identify-unit.manage reset-2fa <対象のユーザー名>
# データベース初期化
# docker exec -it <コンテナID> python -m identify-unit.manage init-db


def setup_schema():
    # 既存のテーブルに totp_secret カカラムが存在するか確認し、なければ追加
    print("Checking schema for 2FA support...")
    try:
        # まずは現在のカラム構成を確認するためにデータを取得
        row = db_session.execute("SELECT * FROM users LIMIT 1").column_names
        if "totp_secret" not in row:
            print("Adding 'totp_secret' column to 'users' table...")
            db_session.execute("ALTER TABLE users ADD totp_secret text")
            print("Schema updated successfully.")
        else:
            print("Schema is already up to date.")
    except Exception as e:
        print(f"Failed to update schema: {e}")

def list_users():
    query = "SELECT username, user_id, totp_secret FROM users"
    try:
        rows = db_session.execute(query)
        print("-" * 85)
        print(f"{'Username':<20} | {'User ID':<40} | {'2FA Status'}")
        print("-" * 85)
        for row in rows:
            # カラムが追加された直後や未設定の場合はNoneが入る
            status = "Enabled" if row.totp_secret else "Disabled"
            print(f"{row.username:<20} | {str(row.user_id):<40} | {status}")
        print("-" * 85)
    except Exception as e:
        print(f"Error fetching user list: {e}")
        print("Tip: Run 'init-db' command first if you haven't updated the schema.")

def reset_2fa(username):
    check_query = "SELECT username FROM users WHERE username = %s"
    user = db_session.execute(check_query, [username]).one()
    
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    update_query = "UPDATE users SET totp_secret = NULL WHERE username = %s"
    db_session.execute(update_query, [username])
    print(f"Success: 2FA has been reset for user '{username}'.")
    print("The user will be prompted for new setup upon next login.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify-Unit Administrative Tool")
    subparsers = parser.add_subparsers(dest="command")

    # DB初期化（カラム追加）コマンド
    subparsers.add_parser("init-db", help="Initialize or update ScyllaDB schema for 2FA")

    # 一覧表示コマンド
    subparsers.add_parser("list", help="List all users and their 2FA status")

    # 2FAリセットコマンド
    reset_parser = subparsers.add_parser("reset-2fa", help="Reset 2FA for a specific user")
    reset_parser.add_argument("username", help="The username to reset")

    args = parser.parse_args()

    if args.command == "init-db":
        setup_schema()
    elif args.command == "list":
        list_users()
    elif args.command == "reset-2fa":
        reset_2fa(args.username)
    else:
        parser.print_help()