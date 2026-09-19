# Streamlit Cloud Deployment

This app can run locally with SQLite and local screenshot files, but shared testing should use persistent services:

- Neon Postgres for the database
- STRATO HiDrive Object Storage, or another S3-compatible bucket, for screenshots

## Streamlit Cloud Secrets

In Streamlit Cloud, add these as app secrets. Keep `DATABASE_URL` at the root level.

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require"

S3_ENDPOINT_URL = "https://YOUR-STRATO-S3-ENDPOINT"
S3_BUCKET = "YOUR-BUCKET"
S3_ACCESS_KEY_ID = "YOUR-ACCESS-KEY"
S3_SECRET_ACCESS_KEY = "YOUR-SECRET-KEY"
S3_REGION = "eu-central-1"
S3_ADDRESSING_STYLE = "auto"

# Optional. If configured, screenshot records store browser-friendly URLs.
# Otherwise they store s3://bucket/key paths.
S3_PUBLIC_BASE_URL = "https://YOUR-PUBLIC-BASE-URL"
```

## Neon

Use the pooled Neon connection string if available. It should include `sslmode=require`.

## STRATO Storage

This app expects an S3-compatible object storage endpoint. STRATO's HiDrive Object Storage provides access key / secret style credentials. Plain HiDrive REST/OAuth storage is a different API and is not wired here.

## Local Development

If `DATABASE_URL` is not set, the app falls back to:

- `data/kingshot.db`
- `battle_reports/`

That is fine locally, but not reliable on Streamlit Cloud.
