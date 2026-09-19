from __future__ import annotations

import os
from pathlib import Path
import re

import boto3
from botocore.config import Config

from database import REPORTS_DIR


def s3_configured() -> bool:
    required = [
        "S3_ENDPOINT_URL",
        "S3_BUCKET",
        "S3_ACCESS_KEY_ID",
        "S3_SECRET_ACCESS_KEY",
    ]
    return all(os.getenv(key) for key in required)


def storage_label() -> str:
    return "S3-compatible object storage" if s3_configured() else str(REPORTS_DIR.name)


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return cleaned or "battle-report"


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        region_name=os.getenv("S3_REGION", "eu-central-1"),
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": os.getenv("S3_ADDRESSING_STYLE", "auto")},
        ),
    )


def save_uploaded_file(upload, experiment_code: str, index: int) -> str:
    suffix = Path(upload.name).suffix.lower() or ".png"
    object_name = f"{experiment_code}_{index}_{safe_filename(upload.name)}"
    if Path(object_name).suffix.lower() != suffix:
        object_name = f"{object_name}{suffix}"

    if s3_configured():
        key = f"battle_reports/{object_name}"
        s3_client().put_object(
            Bucket=os.environ["S3_BUCKET"],
            Key=key,
            Body=upload.getvalue(),
            ContentType=upload.type or "application/octet-stream",
        )
        public_base_url = os.getenv("S3_PUBLIC_BASE_URL", "").rstrip("/")
        if public_base_url:
            return f"{public_base_url}/{key}"
        return f"s3://{os.environ['S3_BUCKET']}/{key}"

    REPORTS_DIR.mkdir(exist_ok=True)
    target = REPORTS_DIR / object_name
    target.write_bytes(upload.getbuffer())
    return str(target)
