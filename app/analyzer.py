from __future__ import annotations

import base64
import json
import os
from typing import Any

from dotenv import load_dotenv
from perplexity import Perplexity

from .prompt import BASE_PROMPT, PRESCRIPTION_SCHEMA, build_user_prompt

load_dotenv()

MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")
API_KEY = os.getenv("PERPLEXITY_API_KEY")
client = Perplexity(api_key=API_KEY) if API_KEY else None


_ALLOWED_MIME = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
}


def _guess_mime(filename: str | None) -> str:
    if not filename:
        return "image/png"
    _, ext = os.path.splitext(filename.lower())
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "image/png")


def _to_data_uri(image_bytes: bytes, content_type: str | None, filename: str | None) -> str:
    mime = (content_type or "").split(";")[0].strip().lower() or _guess_mime(filename)
    if mime not in _ALLOWED_MIME:
        raise ValueError("Unsupported image type. Use PNG, JPG, WEBP, or GIF.")

    if len(image_bytes) > 50 * 1024 * 1024:
        raise ValueError("Image too large. Please keep files under 50MB.")

    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def analyze_prescription(
    image_bytes: bytes | None,
    raw_text: str | None,
    filename: str | None = None,
    content_type: str | None = None,
) -> dict[str, Any]:
    if not image_bytes and not raw_text:
        raise ValueError("Upload an image or paste text.")
    if client is None:
        raise RuntimeError("Missing PERPLEXITY_API_KEY environment variable.")

    prompt = build_user_prompt(raw_text)
    if image_bytes:
        data_uri = _to_data_uri(image_bytes, content_type, filename)
        content: Any = [
            {"type": "text", "text": f"{BASE_PROMPT}\n\n{prompt}"},
            {"type": "image_url", "image_url": {"url": data_uri}},
        ]
    else:
        content = f"{BASE_PROMPT}\n\n{prompt}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": content}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "prescriptionextract",
                "schema": PRESCRIPTION_SCHEMA,
            },
        },
    )

    output_text = response.choices[0].message.content
    if not output_text:
        raise RuntimeError("No output returned from the model.")

    return json.loads(output_text)
