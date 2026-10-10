#!/usr/bin/env python3
"""
Zenn記事用の解説イラストを Microsoft Foundry にデプロイ済みの画像生成モデルで生成する。

使い方:
    python generate_illustration.py --subject "Cosmos DBにベクトルを保存し検索するAIエージェント" \
        --output ../../../images/{slug}/cosmosdb-vector-search.png

環境変数:
    AZURE_FOUNDRY_IMAGE_API_KEY (必須)   Foundryリソースのキー
    AZURE_FOUNDRY_IMAGE_ENDPOINT (任意)  例: https://ai-poc-eastus2-resource.openai.azure.com/
    AZURE_FOUNDRY_IMAGE_DEPLOYMENT (任意) 例: gpt-image-2.5-flare
    AZURE_FOUNDRY_IMAGE_API_VERSION (任意) 例: 2025-04-01-preview

APIキーの取得方法（Azure CLIログイン済みが前提）:
    az cognitiveservices account keys list \
        --name ai-poc-eastus2-resource --resource-group rg-ai-poc-eastus2 \
        --query key1 -o tsv

利用可能なデプロイの確認・変更が必要な場合:
    az cognitiveservices account deployment list \
        --name ai-poc-eastus2-resource --resource-group rg-ai-poc-eastus2 -o table

既存画像の一部だけ直したい場合（誤字の修正など）は --input-image を付ける。images/edits を使い、
--subject は「ここだけ直す、他は変えない」という編集指示になる（スタイルプリセットは付かない）。
    PYTHONUTF8=1 python generate_illustration.py --input-image images/{slug}/a.png \
        --subject "Change only ...; keep everything else identical" \
        --output images/{slug}/a.png --size auto --quality high

Windows注意: --subject に日本語を渡すと既定のコンソールエンコーディングで文字化けすることがある。
必ず PYTHONUTF8=1 を付けて実行する。
--subject-file にUTF-8のファイルを渡せば、この問題は起きない。記事全文のような長文もこちらで渡す。
    PYTHONUTF8=1 python generate_illustration.py --subject "..." --output ...
"""

import argparse
import base64
import os
import sys

import requests

DEFAULT_ENDPOINT = "https://ai-poc-eastus2-resource.openai.azure.com/"
DEFAULT_DEPLOYMENT = "gpt-image-2.5-flare"
DEFAULT_API_VERSION = "2025-04-01-preview"

# 記事の解説画像として使いやすいスタイルプリセット。
# sketch/flat は雰囲気重視のメタファー用途なので文字が崩れやすい "no text" を必ず入れる。
# labeled は具体的なラベル・数値を画像自体に入れて説明力を上げたい場合に使う（日本語・英語とも高精度で生成できる）。
STYLE_PRESETS = {
    "sketch": (
        "hand-drawn whiteboard sketch style, simple clean line art, "
        "marker doodle illustration, soft pastel colors, flat clean white background, "
        "no text, no letters, no words, no logos"
    ),
    "flat": (
        "flat vector illustration, minimal geometric shapes, soft pastel color palette, "
        "clean white background, no text, no letters, no words"
    ),
    "labeled": (
        "a hand-drawn whiteboard explainer diagram, like a teacher's study note, "
        "with clear bold text labels and short descriptive caption phrases explaining each element "
        "(not just single-word labels; correct legible characters, not garbled, simple common characters only), "
        "soft pastel colors, flat clean white background, minimal line art"
    ),
}


def build_prompt(subject: str, style: str) -> str:
    style_text = STYLE_PRESETS.get(style, style)
    return f"{subject}, {style_text}"


def generate_images(prompt: str, size: str, quality: str, n: int, input_image: str | None = None) -> list[bytes]:
    api_key = os.environ.get("AZURE_FOUNDRY_IMAGE_API_KEY")
    if not api_key:
        print(
            "エラー: 環境変数 AZURE_FOUNDRY_IMAGE_API_KEY が未設定です。\n"
            "  az cognitiveservices account keys list --name <resource> "
            "--resource-group <rg> --query key1 -o tsv で取得してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    endpoint = os.environ.get("AZURE_FOUNDRY_IMAGE_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")
    deployment = os.environ.get("AZURE_FOUNDRY_IMAGE_DEPLOYMENT", DEFAULT_DEPLOYMENT)
    api_version = os.environ.get("AZURE_FOUNDRY_IMAGE_API_VERSION", DEFAULT_API_VERSION)

    fields = {"prompt": prompt, "n": n, "size": size, "quality": quality, "output_format": "png"}
    base = f"{endpoint}/openai/deployments/{deployment}/images"

    if input_image:
        with open(input_image, "rb") as f:
            resp = requests.post(
                f"{base}/edits?api-version={api_version}",
                headers={"Api-Key": api_key},
                files={"image": (os.path.basename(input_image), f, "image/png")},
                data=fields,
                timeout=180,
            )
    else:
        resp = requests.post(
            f"{base}/generations?api-version={api_version}",
            headers={"Api-Key": api_key, "Content-Type": "application/json"},
            json=fields,
            timeout=180,
        )
    if resp.status_code != 200:
        print(f"エラー: 画像生成に失敗しました (status={resp.status_code})", file=sys.stderr)
        print(resp.text[:2000], file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    return [base64.b64decode(item["b64_json"]) for item in data["data"]]


def save_images(images: list[bytes], output_path: str) -> list[str]:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    saved = []
    root, ext = os.path.splitext(output_path)
    for i, img_bytes in enumerate(images):
        path = output_path if len(images) == 1 else f"{root}-{i + 1}{ext}"
        with open(path, "wb") as f:
            f.write(img_bytes)
        saved.append(path)
    return saved


def main():
    parser = argparse.ArgumentParser(description="Foundryの画像生成モデルでZenn記事用のイラストを生成する")
    parser.add_argument("--subject", help="説明したい内容（日本語可。英語の方が精度が高い傾向）")
    parser.add_argument("--subject-file", help="--subject の代わりに、UTF-8のテキストファイルからプロンプトを読み込む。記事全文のような長文を渡すときに使う")
    parser.add_argument("--output", required=True, help="保存先パス（例: images/{slug}/overview.png）")
    parser.add_argument("--style", default="sketch", choices=list(STYLE_PRESETS.keys()), help="画風プリセット（デフォルト: sketch。ラベル・数値を画像に入れたい場合は labeled を使い --subject にラベル文言も書く）")
    parser.add_argument("--size", default="1024x1024", choices=["1024x1024", "1024x1536", "1536x1024", "auto"])
    parser.add_argument("--quality", default="medium", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--n", type=int, default=1, help="生成枚数（バリエーション比較用）")
    parser.add_argument("--raw-prompt", action="store_true", help="--subject をスタイル加工せずそのままプロンプトとして使う")
    parser.add_argument("--input-image", help="既存画像を編集する場合の元画像パス。指定すると --subject は編集指示になり、スタイルプリセットは付かない")
    args = parser.parse_args()

    if args.subject_file:
        with open(args.subject_file, encoding="utf-8") as f:
            subject = f.read()
    elif args.subject:
        subject = args.subject
    else:
        parser.error("--subject か --subject-file のどちらかが必要です")

    prompt = subject if (args.raw_prompt or args.input_image) else build_prompt(subject, args.style)
    shown = prompt if len(prompt) <= 600 else f"{prompt[:600]}... (全{len(prompt)}文字)"
    print(f"prompt: {shown}")

    images = generate_images(prompt, args.size, args.quality, args.n, args.input_image)
    saved = save_images(images, args.output)
    for path in saved:
        print(f"saved: {path}")


if __name__ == "__main__":
    main()
