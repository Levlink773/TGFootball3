#!/usr/bin/env bash
# Verification: restart twice; dedup guard must prevent any reminder re-send.
set -euo pipefail
KEY=~/.ssh/footballblitz_vps
HOST=root@football-blitz.online
SSH="ssh -i $KEY $HOST"

$SSH "systemctl restart footballgame"; sleep 20
$SSH "systemctl restart footballgame"; sleep 90
$SSH "systemctl is-active footballgame"
$SSH "journalctl -u footballgame --since '3 minutes ago' --no-pager | grep -Ei 'failed|exited' || echo 'NO CRASHES'"
echo "Check the client chat: there must be ZERO new 'Не забудьте отримати нагороди' messages."
