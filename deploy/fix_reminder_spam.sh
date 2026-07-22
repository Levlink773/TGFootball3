#!/usr/bin/env bash
# Fix for 2026-07-22 reminder spam: broken .env WEBAPP_PORT line (crash loop)
# + deploy notified-date dedup guard. Run from repo root.
set -euo pipefail

KEY=~/.ssh/footballblitz_vps
HOST=root@football-blitz.online
DIR=/root/footballgame
SSH="ssh -i $KEY $HOST"

echo "== 1. Fix .env (missing newline made WEBAPP_PORT invalid -> boot crash loop) =="
$SSH "cp -n $DIR/.env $DIR/.env.bak-20260722 && python3 - <<'EOF'
p = '$DIR/.env'
s = open(p).read()
bad = 'WEBAPP_PORT=3002WEBAPP_ORIGIN=https://app.football-blitz.online'
if bad in s:
    open(p, 'w').write(s.replace(bad, 'WEBAPP_PORT=3002\nWEBAPP_ORIGIN=https://app.football-blitz.online'))
    print('env fixed')
else:
    print('env already fixed')
EOF"

echo "== 2. Upload changed files =="
scp -i "$KEY" \
    schedulers/scheduler_education.py \
    "$HOST:$DIR/schedulers/scheduler_education.py"
scp -i "$KEY" \
    services/character_service.py \
    "$HOST:$DIR/services/character_service.py"
scp -i "$KEY" \
    database/models/reminder_character.py \
    "$HOST:$DIR/database/models/reminder_character.py"
scp -i "$KEY" \
    config.py \
    "$HOST:$DIR/config.py"
scp -i "$KEY" \
    alembic/versions/b7e2f9c31d84_add_education_reward_notified_date.py \
    "$HOST:$DIR/alembic/versions/"

echo "== 3. Run migration (adds column + backfills spammed users as notified) =="
$SSH "cd $DIR && venv/bin/alembic upgrade head"

echo "== 4. Restart =="
$SSH "systemctl restart footballgame"

echo "== 5. Verify: stable 90s (crash loop died at ~65s), then log check =="
sleep 90
$SSH "systemctl is-active footballgame"
$SSH "journalctl -u footballgame --since '2 minutes ago' --no-pager | grep -Ei 'failed|exited' || echo 'JOURNAL CLEAN'"
$SSH "tail -5 $DIR/bot.log"
echo "== DONE. Restart once more to prove no re-blast: bash deploy/fix_reminder_spam_verify.sh =="
