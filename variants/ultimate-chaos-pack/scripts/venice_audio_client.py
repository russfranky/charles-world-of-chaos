"""Venice AI audio generation client (queue → retrieve → complete)."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import requests

QUEUE_URL = "https://api.venice.ai/api/v1/audio/queue"
RETRIEVE_URL = "https://api.venice.ai/api/v1/audio/retrieve"
COMPLETE_URL = "https://api.venice.ai/api/v1/audio/complete"
QUOTE_URL = "https://api.venice.ai/api/v1/audio/quote"

DEFAULT_SFX_MODEL = "elevenlabs-sound-effects-v2"
DEFAULT_MUSIC_MODEL = "ace-step-15"


class VeniceAudioError(Exception):
    pass


def get_api_key() -> str:
    key = os.environ.get("VENICE_API_KEY") or os.environ.get("VENICE_INFERENCE_KEY")
    if not key:
        raise VeniceAudioError(
            "VENICE_API_KEY not set. Export your Venice inference key:\n"
            "  export VENICE_API_KEY='your-key-here'"
        )
    return key


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }


def quote_audio(*, model: str, duration_seconds: int | None = None) -> float:
    payload: dict = {"model": model}
    if duration_seconds is not None:
        payload["duration_seconds"] = duration_seconds
    resp = requests.post(QUOTE_URL, json=payload, headers=_headers(), timeout=60)
    if resp.status_code >= 400:
        raise VeniceAudioError(f"Quote failed {resp.status_code}: {resp.text[:300]}")
    return float(resp.json().get("quote", 0))


def queue_audio(
    *,
    model: str,
    prompt: str,
    duration_seconds: int | None = None,
    force_instrumental: bool | None = None,
) -> str:
    payload: dict = {"model": model, "prompt": prompt}
    if duration_seconds is not None:
        payload["duration_seconds"] = duration_seconds
    if force_instrumental is not None:
        payload["force_instrumental"] = force_instrumental

    resp = requests.post(QUEUE_URL, json=payload, headers=_headers(), timeout=60)
    if resp.status_code == 401:
        raise VeniceAudioError("Venice API authentication failed — check VENICE_API_KEY")
    if resp.status_code == 402:
        raise VeniceAudioError("Venice API insufficient balance")
    if resp.status_code >= 400:
        raise VeniceAudioError(f"Queue failed {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    queue_id = data.get("queue_id")
    if not queue_id:
        raise VeniceAudioError(f"No queue_id in response: {data}")
    return queue_id


def retrieve_audio(
    *,
    model: str,
    queue_id: str,
    poll_interval: float = 3.0,
    timeout: float = 300.0,
) -> tuple[bytes, str]:
    """Poll until audio is ready. Returns (raw_bytes, content_type)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.post(
            RETRIEVE_URL,
            json={"queue_id": queue_id, "model": model},
            headers=_headers(),
            timeout=120,
        )
        content_type = resp.headers.get("Content-Type", "")

        if "audio" in content_type or "octet-stream" in content_type:
            return resp.content, content_type

        if resp.status_code >= 400:
            raise VeniceAudioError(f"Retrieve failed {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        if data.get("status") == "PROCESSING":
            time.sleep(poll_interval)
            continue

        raise VeniceAudioError(f"Unexpected retrieve response: {data}")

    raise VeniceAudioError(f"Timed out waiting for audio queue_id={queue_id}")


def complete_audio(*, model: str, queue_id: str) -> None:
    requests.post(
        COMPLETE_URL,
        json={"queue_id": queue_id, "model": model},
        headers=_headers(),
        timeout=60,
    )


def convert_to_ogg(src_bytes: bytes, dest: Path, *, trim_seconds: float | None = None) -> None:
    """Write raw audio bytes to a temp file and convert to OGG Vorbis."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_bytes(src_bytes)

    cmd = ["ffmpeg", "-y", "-i", str(tmp)]
    if trim_seconds is not None:
        cmd.extend(["-t", str(trim_seconds)])
    cmd.extend(["-c:a", "libvorbis", "-q:a", "4", str(dest)])

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        raise VeniceAudioError(f"ffmpeg failed: {exc.stderr.decode()[:500]}") from exc
    finally:
        tmp.unlink(missing_ok=True)


def generate_audio_to_ogg(
    *,
    model: str,
    prompt: str,
    dest: Path,
    duration_seconds: int | None = None,
    force_instrumental: bool | None = None,
    trim_seconds: float | None = None,
) -> Path:
    queue_id = queue_audio(
        model=model,
        prompt=prompt,
        duration_seconds=duration_seconds,
        force_instrumental=force_instrumental,
    )
    raw, _ = retrieve_audio(model=model, queue_id=queue_id)
    complete_audio(model=model, queue_id=queue_id)
    convert_to_ogg(raw, dest, trim_seconds=trim_seconds or duration_seconds)
    return dest
