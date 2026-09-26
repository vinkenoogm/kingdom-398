# Streamlit Cloud Deployment

This app can run locally with SQLite and local screenshot files, but shared testing should use persistent services:

- Neon Postgres for the database
- STRATO webspace via SFTP for screenshots

## Streamlit Cloud Secrets

In Streamlit Cloud, add these as app secrets. Keep all values at the root level.

```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require"

SFTP_HOST = "YOUR-STRATO-SFTP-HOST"
SFTP_PORT = "22"
SFTP_USERNAME = "YOUR-SFTP-USERNAME"
SFTP_PASSWORD = "YOUR-SFTP-PASSWORD"
SFTP_REMOTE_DIR = "/battle-reports"

# Optional. Use this only if the SFTP folder is web-accessible.
# If configured, screenshot records store clickable browser URLs.
SFTP_PUBLIC_BASE_URL = "https://YOUR-DOMAIN/battle-reports"
```

## Neon

Use the pooled Neon connection string if available. It should include `sslmode=require`.

## STRATO Webspace

Use the SFTP/SSH credentials from STRATO Hosting:

- host/server
- port, usually `22`
- username
- password
- remote folder path

If your STRATO webspace exposes the folder publicly through your domain, set `SFTP_PUBLIC_BASE_URL`. Otherwise the app will store the remote SFTP path in the screenshots table.

## Local Development

If `DATABASE_URL` is not set, the app falls back to:

- `data/kingshot.db`
- `battle_reports/`

That is fine locally, but not reliable on Streamlit Cloud.
