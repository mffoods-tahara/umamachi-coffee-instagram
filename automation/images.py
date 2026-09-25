"""投稿画像一覧。GitHub Pages 上の公開URLを使う（Instagram Graph API要件）。"""
from pathlib import Path

# GitHub Pages: https://mffoods-tahara.github.io/umamachi-coffee-instagram/images/
BASE_URL = "https://mffoods-tahara.github.io/umamachi-coffee-instagram/images/"

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"

# リポジトリ内 images/ を走査（追加したら自動で対象になる）
IMAGES = sorted(
    p.name
    for p in IMAGES_DIR.iterdir()
    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
)

if not IMAGES:
    raise RuntimeError(f"投稿画像がありません: {IMAGES_DIR}")
