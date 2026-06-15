"""Load .env and validate Venice API key configuration."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = REPO_ROOT / ".env"

PLACEHOLDER_PATTERNS = (
    re.compile(r"your[-_]?key", re.I),
    re.compile(r"your[-_]?venice", re.I),
    re.compile(r"changeme", re.I),
    re.compile(r"xxx+", re.I),
)


def load_project_env() -> None:
    """Load .env from repo root if present."""
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)


def warn_if_placeholder_key() -> None:
    key = os.environ.get("VENICE_API_KEY") or os.environ.get("VENICE_INFERENCE_KEY") or ""
    if not key:
        return
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(key):
            print(
                "Warning: VENICE_API_KEY looks like a placeholder — set a real key in .env",
                file=sys.stderr,
            )
            return


def init_env() -> None:
    load_project_env()
    warn_if_placeholder_key()
