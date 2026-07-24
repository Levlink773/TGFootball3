#!/usr/bin/env bash
# Atomic webapp deploy — fixes the "black screen during update" bug.
#
# The old deploy did `rm -rf webapp/dist && tar -x`, leaving a ~1-2s window where
# nginx's root had no index.html → any user opening the Mini App then got a black
# screen. This ships to a temp dir and rsyncs into place with NO --delete, so:
#   - index.html is replaced atomically (rsync writes temp + rename)
#   - old hashed assets stay, so clients that already loaded an older index.html
#     keep working instead of 404-ing a missing JS chunk
# Run AFTER a production build (webapp/dist must hold the prod bundle).
set -euo pipefail

KEY="${FOOTBALL_VPS_KEY:-$HOME/.ssh/footballblitz_vps}"
VPS="${FOOTBALL_VPS:-root@46.202.190.222}"
DEST=/root/footballgame/webapp/dist
REPO="$(cd "$(dirname "$0")/.." && pwd)"

[ -f "$REPO/webapp/dist/index.html" ] || { echo "ERROR: build webapp first (no dist/index.html)"; exit 1; }
if grep -q "127.0.0.1" "$REPO"/webapp/dist/assets/index-*.js 2>/dev/null; then
  echo "ERROR: dist bundle points at a local API URL — rebuild with the prod VITE_API_URL"; exit 1
fi

COPYFILE_DISABLE=1 tar -czf /tmp/wdist.tgz -C "$REPO" webapp/dist
scp -i "$KEY" -o StrictHostKeyChecking=no /tmp/wdist.tgz "$VPS:/root/wdist.tgz"

ssh -i "$KEY" -o StrictHostKeyChecking=no "$VPS" "
  set -e
  rm -rf /tmp/wdeploy && mkdir -p /tmp/wdeploy
  tar -xzf /root/wdist.tgz -C /tmp/wdeploy 2>/dev/null
  rsync -a /tmp/wdeploy/webapp/dist/ $DEST/
  rm -rf /tmp/wdeploy /root/wdist.tgz
  echo \"deployed bundle: \$(grep -o 'index-[A-Za-z0-9_]*\.js' $DEST/index.html)\"
"
echo "done."
