# 馬町珈琲 Instagram 自動投稿

京都・五条の自家焙煎珈琲店「馬町珈琲」向け。毎日10:00（JST）に画像と文面をローテーションして投稿する（**API課金なし**）。

## 仕組み

1. `images/` の写真を順番に選ぶ
2. `automation/templates.py` の文面を順番に選ぶ
3. Instagram Graph API で投稿
4. GitHub Actions が毎日定時実行（手動実行も可）

## 必要な GitHub Secrets（2つだけ）

| Name | 内容 |
|------|------|
| `IG_ACCESS_TOKEN` | 馬町の長期トークン |
| `IG_USER_ID` | 馬町の Instagram Business Account ID |

設定先: https://github.com/mffoods-tahara/umamachi-coffee-instagram/settings/secrets/actions

## 文面の追加・編集

`automation/templates.py` の `TEMPLATES` に文章を足す／直して push すればOK。

## 画像の追加

`images/` に JPEG を置いて push。次回からローテ対象になる。

## 投稿時刻

`.github/workflows/instagram-auto-post.yml` の cron（UTC）。現在 `0 1 * * *` = 毎日 10:00 JST。
