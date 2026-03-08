# TG Football — Deployment Guide

## Prerequisites

- VPS with Ubuntu 22.04+ (minimum 2 vCPU, 4GB RAM)
- Domain name pointed to the server IP
- MySQL 8.0+
- Python 3.11+
- Nginx
- Certbot

## Step 1: Server Setup

```bash
# Install system packages
sudo apt update
sudo apt install python3.11 python3.11-venv mysql-server nginx certbot python3-certbot-nginx

# Create app user
sudo useradd -m -s /bin/bash tgfootball
```

## Step 2: Database Setup

```bash
sudo mysql -u root <<EOF
CREATE DATABASE tg_football CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tg_football_user'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON tg_football.* TO 'tg_football_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

## Step 3: Deploy Application

```bash
# Clone repo to /opt/tg-football
sudo mkdir -p /opt/tg-football
sudo chown tgfootball:tgfootball /opt/tg-football

sudo -u tgfootball bash <<'EOF'
cd /opt/tg-football
git clone <repo-url> .
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF

# Copy and edit .env
sudo -u tgfootball cp /opt/tg-football/.env.example /opt/tg-football/.env
# Edit .env with production values:
#   DB_LOGIN=tg_football_user
#   DB_PASSWORD=YOUR_STRONG_PASSWORD
#   BOT_TOKEN=<new token from BotFather>
#   TOKEN_MONOBANK=<your monobank token>
#   CALLBACK_URL_WEBHOOK_*=https://yourdomain.com/...
#   WEBAPP_HOST=127.0.0.1
sudo -u tgfootball nano /opt/tg-football/.env
```

## Step 4: Run Migrations

```bash
sudo -u tgfootball bash -c 'cd /opt/tg-football && source venv/bin/activate && alembic upgrade head'
```

## Step 5: SSL + Nginx

```bash
# Get SSL certificate
sudo certbot certonly --nginx -d yourdomain.com

# Install nginx config
sudo cp /opt/tg-football/deploy/nginx.conf /etc/nginx/sites-available/tg-football
# Edit server_name to your actual domain
sudo nano /etc/nginx/sites-available/tg-football
sudo ln -s /etc/nginx/sites-available/tg-football /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Step 6: Systemd Service

```bash
sudo cp /opt/tg-football/deploy/tg-football.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tg-football
sudo systemctl start tg-football

# Check status
sudo systemctl status tg-football
sudo journalctl -u tg-football -f
```

## Step 7: Automated Backups

```bash
# Add to crontab (daily at 3 AM)
echo "0 3 * * * mysqldump -u tg_football_user -p'YOUR_STRONG_PASSWORD' tg_football | gzip > /opt/backups/tg_football_\$(date +\%Y\%m\%d).sql.gz" | sudo crontab -u tgfootball -

sudo mkdir -p /opt/backups
sudo chown tgfootball:tgfootball /opt/backups
```

## Verification

After deployment, verify:
1. `sudo systemctl status tg-football` — service is active
2. Send `/start` to the bot in Telegram — it should respond
3. Check `https://yourdomain.com/` returns a response (payment webhook endpoint)
4. `tail -f /opt/tg-football/error_logs.log` — no critical errors
