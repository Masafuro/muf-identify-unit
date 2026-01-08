# muf-identify-unit

## 概要
muf-identify-unitは、MUF（Masafuro Unit Framework）アーキテクチャにおいて認証およびセッション管理を担当するゲートウェイユニットです。ユーザーの資格情報をMUFネットワークから隔離されたScyllaDBで保護し、多要素認証（MFA）を通過したユーザーのみをシステム全体へ公開する仕組みを採用しています。

## MUFライブラリ及びコアユニット
[MUF:Memory Unit Framework](https://github.com/Masafuro/MUF)

## システム構成
| コンポーネント | 役割 | 備考 |
| :--- | :--- | :--- |
| **FastAPI** | Webインターフェース | 非同期処理による高効率なリクエストハンドリング |
| **ScyllaDB** | 永続データストレージ | ユーザーID、bcryptハッシュ化パスワード、2FA秘密鍵の保持 |
| **Redis** | セッション・メッセージング | MUFネットワークの共有メモリ空間として機能 |
| **Bootstrap 5** | フロントエンドUI | レスポンシブデザインによるマルチデバイス対応 |

## 環境設定（.env）
| 変数名 | 説明 | デフォルト値 |
| :--- | :--- | :--- |
| REDIS_HOST | MUF基盤となるRedisのホスト名 | muf-redis |
| SCYLLA_HOST | ユーザー情報を保持するScyllaDBのホスト名 | muf-scylla |
| SCYLLA_KEYSPACE | ScyllaDB内で使用するキースペース名 | muf_auth |
| SESSION_TTL | セッションの有効期限（秒） | 3600 |
| COOKIE_SECURE | CookieのSecure属性（HTTPS環境ではTrue） | False |
| LOGIN_REDIRECT_URL | 認証成功後のリダイレクト先URL | (要指定) |

## MUFネットワーク仕様
### 状態公開パス
muf/identify-unit/keep/{session_id}

### 公開データ構造（JSON）
| フィールド名 | 型 | 説明 |
| :--- | :--- | :--- |
| username | string | ログインしたユーザーの名称 |
| user_id | string | ScyllaDB上の不変のユーザー識別子（UUID） |
| login_at | string | ISO8601形式のログイン日時 |

## ファイル構成
本ユニットは責務を分離するために以下の階層構造をとっています。

* **identify-unit/routers/**
    * `register.py`: ユーザー新規登録ロジック（bcryptハッシュ化）
    * `login.py`: パスワード認証および2FA分岐処理
    * `totp_setup.py`: 2FA初期設定およびQRコード生成
    * `totp_verify.py`: 2FAコード検証処理
* **identify-unit/services/**
    * `auth_service.py`: Redis/MUFネットワークへのセッション登録共通処理
* **identify-unit/templates/**
    * 各画面のHTMLテンプレート（Jinja2）
* `database.py`: ScyllaDBおよびRedisへの接続定義と初期化
* `manage.py`: データベース管理・リカバリ用CLIツール

## 管理コマンド（manage.py）
ScyllaDBのメンテナンスは、Dockerコンテナ内から`manage.py`を介して行います。

* **DB初期化・スキーマ更新**
    `python -m identify-unit.manage init-db`
* **ユーザー一覧と2FA設定状況の確認**
    `python -m identify-unit.manage list`
* **特定のユーザーの2FA設定をリセット**
    `python -m identify-unit.manage reset-2fa <username>`

## セッションCookie仕様
| 項目 | 仕様 | 備考 |
| :--- | :--- | :--- |
| **session_id** | 本セッション | 2FA完了後に発行される認証トークン |
| **temp_user** | 一時Cookie | 2FA完了までユーザーを識別（5分で自動消滅） |
| **HttpOnly** | 有効 (True) | JavaScriptからのアクセスを禁止 |
| **Secure** | 変数依存 | `.env`の`COOKIE_SECURE`設定に従う |
| **SameSite** | Lax | CSRF対策と利便性を両立 |

## 導入と起動
1. Dockerfileからイメージをビルドします。bcryptの互換性のためにバージョン3系を固定して利用します。
2. `docker-compose up`を実行してサービスを開始します。
3. 初回起動時、または2FA機能の追加時には、管理コマンド`init-db`を実行してScyllaDBのスキーマを最新状態に更新してください。