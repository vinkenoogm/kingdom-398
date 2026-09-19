from __future__ import annotations

import os
from pathlib import Path
import posixpath
import re

import paramiko

from database import REPORTS_DIR


def sftp_configured() -> bool:
    required = [
        "SFTP_HOST",
        "SFTP_USERNAME",
        "SFTP_PASSWORD",
        "SFTP_REMOTE_DIR",
    ]
    return all(os.getenv(key) for key in required)


def storage_label() -> str:
    return "STRATO webspace via SFTP" if sftp_configured() else str(REPORTS_DIR.name)


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return cleaned or "battle-report"


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    current = ""
    for part in remote_dir.strip("/").split("/"):
        if not part:
            continue
        current = f"{current}/{part}"
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)


def upload_via_sftp(upload, remote_name: str) -> str:
    host = os.environ["SFTP_HOST"]
    port = int(os.getenv("SFTP_PORT", "22"))
    username = os.environ["SFTP_USERNAME"]
    password = os.environ["SFTP_PASSWORD"]
    remote_dir = os.environ["SFTP_REMOTE_DIR"].rstrip("/")

    transport = paramiko.Transport((host, port))
    try:
        transport.connect(username=username, password=password)
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            ensure_remote_dir(sftp, remote_dir)
            remote_path = posixpath.join(remote_dir, remote_name)
            with sftp.file(remote_path, "wb") as remote_file:
                remote_file.write(upload.getvalue())
    finally:
        transport.close()

    public_base_url = os.getenv("SFTP_PUBLIC_BASE_URL", "").rstrip("/")
    if public_base_url:
        return f"{public_base_url}/{remote_name}"
    return remote_path


def save_uploaded_file(upload, experiment_code: str, index: int) -> str:
    suffix = Path(upload.name).suffix.lower() or ".png"
    remote_name = f"{experiment_code}_{index}_{safe_filename(upload.name)}"
    if Path(remote_name).suffix.lower() != suffix:
        remote_name = f"{remote_name}{suffix}"

    if sftp_configured():
        return upload_via_sftp(upload, remote_name)

    REPORTS_DIR.mkdir(exist_ok=True)
    target = REPORTS_DIR / remote_name
    target.write_bytes(upload.getbuffer())
    return str(target)
