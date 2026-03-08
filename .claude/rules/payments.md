---
paths:
  - "webhook_api/**"
  - "api/**"
  - "main.py"
---

# Payment Webhook Rules

- Webhook handlers in `webhook_api/` are registered as aiohttp routes in `main.py`. Adding a new handler requires registering it there.
- Each purchase type has its own webhook URL (configured via `CALLBACK_URL_WEBHOOK_*` env vars) and its own handler file.
- Monobank token is in `TOKEN_MONOBANK` env var. Never hardcode payment credentials.
