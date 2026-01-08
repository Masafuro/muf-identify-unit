# 開発情報

## 開発コマンド

mufアップデート
> git submodule update --remote

muf-redis立ち上げ
> docker compose up -d muf-redis

muf-monitor立ち上げ
> docker compose run --rm muf-monitor

identify-unit立ち上げ
> cd identify-unit
> docker compose up

ブラウザ動作確認
> localhost:8000