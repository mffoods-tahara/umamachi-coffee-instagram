# 馬町珈琲 Instagram 自動投稿

京都・五条の自家焙煎珈琲店「馬町珈琲」向け。毎日10:00（JST）に画像をローテーションし、AIでキャプションを生成して投稿する。

## 仕組み

1. `images/` の写真を順番に選ぶ
2. OpenAI（Vision）で写真に合う日本語キャプションを生成
3. Instagram Graph API で投稿
4. GitHub Actions が毎日定時実行（手動実行も可）

画像は GitHub Pages 経由で公開URLにする（APIの要件）。

## 初回セットアップ

### 1. このリポジトリを GitHub に置く

リポジトリ名想定: `mffoods-tahara/umamachi-coffee-instagram`

Settings → Pages → Source: **Deploy from a branch** → `main` / `/ (root)`

公開画像の例:

`https://mffoods-tahara.github.io/umamachi-coffee-instagram/images/IMG_4146.jpg`

### 2. Instagram API（馬町アカウント用）

前提: ビジネスアカウント ＋ Facebookページ連携済み（済み）

1. [Meta for Developers](https://developers.facebook.com/) でアプリ作成（または既存アプリ）
2. Instagram Graph API / Instagram API with Instagram Login を追加
3. 馬町の Instagram ユーザーID（`IG_USER_ID`）と長期アクセストークン（`IG_ACCESS_TOKEN`）を取得

ホィップラテ側で同じ手順をやっている場合、**別アカウント用にトークンとユーザーIDを取り直す**（同じSecretsを流用しない）。

トークンが Facebook Login 由来なら、Actions / `.env` に次を追加:

```
IG_GRAPH_API=https://graph.facebook.com/v21.0
```

### 3. OpenAI APIキー

[OpenAI API Keys](https://platform.openai.com/api-keys) でキーを発行（モデル既定: `gpt-4o-mini`）。

### 4. GitHub Secrets

Repository → Settings → Secrets and variables → Actions:

| Name | 内容 |
|------|------|
| `IG_ACCESS_TOKEN` | 馬町の長期トークン |
| `IG_USER_ID` | 馬町の Instagram Business Account ID |
| `OPENAI_API_KEY` | OpenAI APIキー |

### 5. 動作確認

Actions → **Instagram Auto Post** → Run workflow

ローカル確認（投稿せずキャプションだけ）:

```powershell
cd automation
copy .env.example .env
# .env を編集
pip install -r requirements.txt
$env:DRY_RUN="1"
python post_instagram.py
```

## 画像の追加

`馬町\馬町珈琲_IG_…\馬町珈琲画像` に新しい写真を入れたら:

1. JPEG/PNG を `images/` にコピー（長辺1080px・JPEG推奨）
2. `git add` → `commit` → `push`

次回以降の投稿で自動的にローテーション対象になる。

## 投稿時刻の変更

`.github/workflows/instagram-auto-post.yml` の cron を変更（UTC表記）。

- 現在: `0 1 * * *` = 毎日 10:00 JST
- 例）14:00 JST → `0 5 * * *`

## フォルダ構成

```
umamachi-coffee-instagram/
  images/                 # 公開用画像
  automation/
    post_instagram.py     # 投稿本体
    generate_caption.py   # AI文面
    brand.py              # 店舗トーン
    images.py             # 画像一覧
    state.json            # ローテ位置
  .github/workflows/
    instagram-auto-post.yml
```
