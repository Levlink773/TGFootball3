# Deployment

TG Football lives on GCP, mirroring the FootballBlitz pattern but in a separate project (`agent-leads-gen`) — the FootballBlitz project (`project-6ee5fc7a-ec32-48d3-ae0`) is client-owned and not under user IAM.

## Server (planned/live)

- **GCP project:** `agent-leads-gen`
- **Zone:** `europe-north2-a` (Stockholm)
- **Machine type:** `e2-medium` (2 vCPU shared, 4 GB RAM)
- **OS:** Debian 12 (bookworm)
- **Disk:** 20 GB pd-standard
- **External IP name:** `tg-football-ip` (static)
- **Instance name:** `tg-football`
- **App user:** `tgfootball`
- **App dir:** `/opt/tg-football`
- **Service:** `tg-football.service` (systemd)
- **DB:** local MySQL, schema `tg_football`

## SSH

GCP VMs created with `enable-oslogin=TRUE` — use `gcloud compute ssh`, not raw SSH:

```bash
PROJECT=agent-leads-gen
ZONE=europe-north2-a
NAME=tg-football

gcloud compute ssh "$NAME" --zone="$ZONE" --project="$PROJECT"
gcloud compute ssh "$NAME" --zone="$ZONE" --project="$PROJECT" --command='sudo journalctl -u tg-football -n 50 --no-pager'
gcloud compute scp local_file "$NAME:~/" --zone="$ZONE" --project="$PROJECT"
```

## First-time provisioning

1. Ensure billing is enabled on `agent-leads-gen` (one-time, requires user)
2. `bash deploy/gcp-create-vm.sh` — creates IP, firewall, VM (idempotent)
3. `gcloud compute scp deploy/bootstrap.sh tg-football:~/ --zone=europe-north2-a --project=agent-leads-gen`
4. `gcloud compute ssh tg-football --zone=europe-north2-a --project=agent-leads-gen --command='bash bootstrap.sh'` — installs system deps, MySQL, creates app user + DB. Outputs generated DB password.
5. Rsync the repo into `/opt/tg-football/` (exclude `.venv`, `venv`, `__pycache__`, `.git`, `error_logs.log`, `graphify-out/`, `src/` if huge)
6. Write `/opt/tg-football/.env` with: DB creds from bootstrap output, `BOT_TOKEN`, `TOKEN_MONOBANK`, `WEBAPP_HOST=127.0.0.1`, `WEBAPP_PORT=3002`. No webhook URLs yet (Monobank webhooks deferred until domain set up).
7. Create venv + install deps + run `alembic upgrade head`
8. Install systemd unit + `systemctl enable --now tg-football`

## Deploy updates (after VM exists)

Pattern from FootballBlitz: SCP changed files → restart service.

```bash
PROJECT=agent-leads-gen
ZONE=europe-north2-a
NAME=tg-football

# 1. rsync changed files (sudo on the receiving side because /opt is root-owned)
rsync -avz --rsync-path='sudo rsync' \
    --exclude='.venv' --exclude='venv' --exclude='__pycache__' \
    --exclude='.git' --exclude='error_logs.log' --exclude='graphify-out' \
    -e "gcloud compute ssh --zone=$ZONE --project=$PROJECT --tunnel-through-iap --" \
    bot/ "$NAME:/opt/tg-football/bot/"

# 2. restart (uses /opt/tg-football/deploy/restart_server.sh)
gcloud compute ssh "$NAME" --zone="$ZONE" --project="$PROJECT" \
    --command='sudo bash /opt/tg-football/deploy/restart_server.sh'
```

## Verification (after every deploy)

1. `gcloud compute ssh tg-football ... --command='sudo systemctl is-active tg-football'` → must return `active`
2. `... --command='sudo journalctl -u tg-football -n 30 --no-pager | grep -iE "error|exception|traceback" || echo CLEAN'`
3. Send `/start` to the bot in Telegram from a test account; confirm welcome message
4. `... --command='sudo tail -20 /opt/tg-football/error_logs.log'`

Never claim "deployed" without those four checks.

## Common gotchas

- `/opt/tg-football` is owned by `tgfootball` (not the SSH user). Rsync needs `--rsync-path='sudo rsync'`.
- `alembic` migrations use `pymysql` (sync) while app uses `aiomysql` (async). `alembic/env.py` reads `.env` to override `alembic.ini` — don't hardcode credentials in `alembic.ini` on the server.
- Python on Debian 12 is 3.11 — confirmed compatible. Don't pin a different Python in `requirements.txt`.
- Monobank webhooks need HTTPS + domain. Until a domain is wired up, the bot can run **polling-only** (BOT_TOKEN works, no webhook URLs needed). The aiohttp app on port 3002 will still start but the URLs in `.env` can be left as `http://localhost:3002/...` placeholders.
- `.env` on the server must NOT be overwritten by rsync. Exclude it explicitly.
