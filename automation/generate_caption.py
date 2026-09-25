"""画像を見て OpenAI でキャプションを生成する。"""
from __future__ import annotations

import base64
import os
from pathlib import Path

from openai import OpenAI

from brand import CAPTION_SYSTEM_PROMPT, HASHTAG_FALLBACK


def _data_url(image_path: Path) -> str:
    raw = image_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    suffix = image_path.suffix.lower()
    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(suffix, "image/jpeg")
    return f"data:{mime};base64,{b64}"


def generate_caption(image_path: Path, model: str | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY が未設定です")

    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0.8,
        max_tokens=400,
        messages=[
            {"role": "system", "content": CAPTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "この写真に合う今日のInstagram投稿文を書いてください。",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": _data_url(image_path)},
                    },
                ],
            },
        ],
    )

    text = (response.choices[0].message.content or "").strip()
    if not text:
        return (
            "京都・五条の街かどで、一杯ずつ手で淹れる自家焙煎珈琲を。\n"
            "街歩きのとちゅうに、ひと休みしませんか。\n\n"
            f"{HASHTAG_FALLBACK}"
        )
    return text
