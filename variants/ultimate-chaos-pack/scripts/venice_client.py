"""Venice AI image generation client for Minecraft texture pipeline."""

from __future__ import annotations

import base64
import os
import time
from pathlib import Path

import requests

from env_loader import init_env

init_env()

API_URL = "https://api.venice.ai/api/v1/image/generate"
DEFAULT_MODEL = "flux-2-pro"
FALLBACK_MODEL = "venice-sd35"

MODEL_ALIASES = {
    "flux": "flux-2-pro",
    "flux-dev": "flux-2-pro",
    "flux-2-pro": "flux-2-pro",
    "flux-2-max": "flux-2-max",
    "sd35": "venice-sd35",
    "venice-sd35": "venice-sd35",
    "dreamshaper": "lustify-sdxl",
    "lustify-sdxl": "lustify-sdxl",
    "gpt-image-2": "gpt-image-2",
    "qwen-image": "qwen-image",
}


class VeniceError(Exception):
    pass


def get_api_key() -> str:
    key = os.environ.get("VENICE_API_KEY") or os.environ.get("VENICE_INFERENCE_KEY")
    if not key:
        raise VeniceError(
            "VENICE_API_KEY not set. Export your Venice inference key:\n"
            "  export VENICE_API_KEY='your-key-here'"
        )
    return key


def generate_image(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    width: int = 1024,
    height: int = 1024,
    style_preset: str | None = None,
    negative_prompt: str = "blurry, smooth, gradient, anti-aliased, photorealistic, 3d render",
    seed: int | None = None,
    timeout: int = 180,
) -> bytes:
    """Generate an image via Venice AI. Returns raw PNG bytes."""
    api_key = get_api_key()
    resolved_model = MODEL_ALIASES.get(model, model)

    payload: dict = {
        "model": resolved_model,
        "prompt": prompt,
        "width": width,
        "height": height,
        "format": "png",
        "negative_prompt": negative_prompt,
        "hide_watermark": True,
    }
    if style_preset:
        payload["style_preset"] = style_preset
    if seed is not None:
        payload["seed"] = seed

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_error: Exception | None = None
    for attempt_model in (resolved_model, FALLBACK_MODEL):
        payload["model"] = attempt_model
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=timeout)
            if resp.status_code == 401:
                raise VeniceError("Venice API authentication failed — check VENICE_API_KEY")
            if resp.status_code == 402:
                raise VeniceError("Venice API insufficient balance")
            if resp.status_code >= 400:
                raise VeniceError(f"Venice API error {resp.status_code}: {resp.text[:500]}")

            data = resp.json()
            images = data.get("images", [])
            if not images:
                raise VeniceError(f"No images in response: {data}")

            raw = base64.b64decode(images[0])
            return raw
        except VeniceError:
            raise
        except Exception as exc:
            last_error = exc
            if attempt_model == FALLBACK_MODEL:
                break
            time.sleep(2)

    raise VeniceError(f"Venice generation failed: {last_error}")


def save_png(data: bytes, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
