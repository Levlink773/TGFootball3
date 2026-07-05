#!/usr/bin/env bash
# =============================================================
# TG Football — server-side deploy/restart helper.
#
# Runs DB migrations BEFORE restarting the service, so the running schema can
# never lag the code again (that "code ahead of DB" drift is what broke club
# creation: the code had the clubs feature while the DB was behind, and — the
# actual incident — code assumed one character per user while the DB had no
# UNIQUE constraint to enforce it). If the migration fails the service is NOT
# restarted, so a bad migration can't ship.
#
# Location on server: /root/footballgame/deploy/restart_server.sh
# Usage (on the VPS): sudo bash /root/footballgame/deploy/restart_server.sh
# =============================================================
set -euo pipefail

SERVICE=footballgame
APP_DIR=/root/footballgame
ALEMBIC="$APP_DIR/venv/bin/alembic"

cd "$APP_DIR"

echo "=== 1/3  Applying DB migrations (alembic upgrade head) ==="
if [ -x "$ALEMBIC" ]; then
    "$ALEMBIC" upgrade head
else
    ./venv/bin/python -m alembic upgrade head
fi
echo "    migrations OK"

echo "=== 2/3  Restarting $SERVICE ==="
systemctl restart "$SERVICE"
sleep 3

echo "=== 3/3  Verifying $SERVICE ==="
if systemctl is-active --quiet "$SERVICE"; then
    echo "SUCCESS: $SERVICE active"
    echo "--- Last 10 journal lines ---"
    journalctl -u "$SERVICE" -n 10 --no-pager
    echo "--- Last 5 error_logs.log lines ---"
    tail -5 "$APP_DIR/error_logs.log" 2>/dev/null || echo "(no error log yet)"
else
    echo "FAILED: $SERVICE is not active. Last 30 journal lines:"
    journalctl -u "$SERVICE" -n 30 --no-pager
    exit 1
fi
