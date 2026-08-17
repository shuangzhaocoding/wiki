#!/bin/sh
set -eu

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"
APP_WORKERS="${APP_WORKERS:-1}"

echo "[entrypoint] start uvicorn ${APP_HOST}:${APP_PORT} workers=${APP_WORKERS}"
cd /wiki-zs
uvicorn app.main:app --host "${APP_HOST}" --port "${APP_PORT}" --workers "${APP_WORKERS}" &
UVICORN_PID=$!

cleanup() {
  kill "${UVICORN_PID}" 2>/dev/null || true
  wait "${UVICORN_PID}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

i=0
while [ "$i" -lt 60 ]; do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${APP_PORT}/api/health', timeout=1)" >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

echo "[entrypoint] start nginx :80"
exec nginx -c /etc/nginx/nginx.conf -g 'daemon off;'
