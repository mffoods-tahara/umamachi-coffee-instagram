"""馬町珈琲 Instagram 自動投稿（画像ローテ + AIキャプション）。"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from generate_caption import generate_caption
from images import BASE_URL, IMAGES, IMAGES_DIR

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / "state.json"
LOG_FILE = BASE_DIR / "post_log.txt"
CAPTION_LOG = BASE_DIR / "caption_log.jsonl"

load_dotenv(BASE_DIR / ".env")

# Instagram Login → graph.instagram.com / Facebook Login → graph.facebook.com/v21.0
GRAPH_API = os.getenv("IG_GRAPH_API", "https://graph.instagram.com/v21.0")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"image_index": -1, "posted": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def wait_until_ready(creation_id: str, access_token: str, timeout: int = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(
            f"{GRAPH_API}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        resp.raise_for_status()
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"メディア処理が失敗しました: {resp.json()}")
        time.sleep(3)
    raise TimeoutError("メディア処理がタイムアウトしました")


def append_caption_log(image_name: str, caption: str, media_id: str | None) -> None:
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "image": image_name,
        "caption": caption,
        "media_id": media_id,
    }
    with CAPTION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    required = ["IG_ACCESS_TOKEN", "IG_USER_ID", "OPENAI_API_KEY"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        msg = f".env / Secrets に次を設定してください: {', '.join(missing)}"
        logging.error(msg)
        raise SystemExit(msg)

    access_token = os.getenv("IG_ACCESS_TOKEN")
    ig_user_id = os.getenv("IG_USER_ID")
    dry_run = os.getenv("DRY_RUN", "").lower() in {"1", "true", "yes"}

    state = load_state()
    image_index = (state.get("image_index", -1) + 1) % len(IMAGES)
    image_name = IMAGES[image_index]
    image_path = IMAGES_DIR / image_name
    image_url = BASE_URL + image_name

    print(f"[{datetime.now()}] 対象画像: {image_name}")
    caption = generate_caption(image_path)
    print("--- 生成キャプション ---")
    print(caption)
    print("----------------------")

    if dry_run:
        append_caption_log(image_name, caption, None)
        print("DRY_RUN=1 のため投稿をスキップしました")
        return

    try:
        create_resp = requests.post(
            f"{GRAPH_API}/{ig_user_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token,
            },
            timeout=60,
        )
        create_resp.raise_for_status()
        creation_id = create_resp.json()["id"]

        wait_until_ready(creation_id, access_token)

        publish_resp = requests.post(
            f"{GRAPH_API}/{ig_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token},
            timeout=60,
        )
        publish_resp.raise_for_status()
        media_id = publish_resp.json().get("id")

        posted = list(state.get("posted", []))
        posted.append(
            {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "image": image_name,
                "media_id": media_id,
            }
        )
        save_state({"image_index": image_index, "posted": posted[-60:]})
        append_caption_log(image_name, caption, media_id)
        logging.info(
            "投稿成功 (image=%s, media_id=%s)",
            image_name,
            media_id,
        )
        print(f"[{datetime.now()}] 投稿成功: {image_name} media_id={media_id}")
    except requests.HTTPError as e:
        logging.error(
            "投稿失敗 (image=%s): %s / %s",
            image_name,
            e,
            e.response.text if e.response is not None else "",
        )
        raise
    except Exception as e:
        logging.error("投稿失敗 (image=%s): %s", image_name, e)
        raise


if __name__ == "__main__":
    main()
