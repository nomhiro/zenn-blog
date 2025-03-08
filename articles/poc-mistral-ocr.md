---
title: "【OCR革命！？】Mistral OCR で生成AIが理解できる構造化データにしよう🚀"
emoji: "📝"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["OCR", "AI", "MistralOCR", "LLM", "RAG"]
published: false
---

# はじめに
RAGの推論を高める要素の1つとして、取得したい情報を検索できるか、検索した情報が生成AIが推論できる状態になっているか。という観点があります。

また、従来の業務データや文書は、手書きやExcel、Powerpointなどを用いて作成された、図表などが多く含まれるデータが多いです。のようなデータをAIが理解できる構造化データに変換するために、OCR技術が活用されています。
例えばAzureサービスを使う場合、DocumentIntelligenceを使ってOCRを行い、Markdown形式に変換することができます。また、GPT4oなどのマルチモーダルなモデルを使うことで、画像データを入力として、文章を生成することができます。DocumentIntelligenceとGPT4oを組み合わせてデータ化することもあります。

この記事では、2025年3月6日に公開された**Mistral OCRを使った、文書のMarkdown化**をPoCします。

# Mistral OCRとは
https://mistral.ai/en/news/mistral-ocr
Mistral OCRは、**ドキュメントをOCR（光学式文字認識）のAPI**で、マルチモーダルドキュメント(スライドや複雑なPDFなど)を入力として受け取るRAGシステムと組み合わせて使用する理想的なモデルです。
画像やPDFを受け取り、その中のイメージ、テキスト、表、数式などを認識し理解し、コンテンツを抽出します。


以下はMistralから公開されている、PDFからテキストと画像を抽出してMarkdownファイルにするデモです。
https://youtu.be/6lRBm0KnzBI

## 特徴
- 2000ページのPDFを処理可能
- プロンプトで指示することにより、ドキュメントから特定の情報を抽出できる。
- Jsonなど構造化された出力にフォーマットできる
- オンプレミスなどの環境にホスティング可能。機密情報を自社のインフラ内で処理できる。

# PoC 🐻‍❄️

## 扱うドキュメント
今回は、以下のPDFを使って、Mistral OCRでMarkdown化を行います。
日本政府が公開している、「令和６年版_科学技術・イノベーション白書」の本文です。
**128ページあり、図や表などが含まれています。**
https://www.mext.go.jp/content/20240611-ope_dev03-000036120-9.pdf

例えば、以下のような図が文章の中に含まれています。
![](/images/poc-mistral-ocr/2025-03-09-00-24-49.png)

表については、以下のようなものが含まれています。
![](/images/poc-mistral-ocr/2025-03-09-00-37-00.png)

## Mistral AI のAPIキーを取得
Mistral OCRを使うためには、Mistral AIのAPIキーが必要です。
まだAPIKeyを持っていない場合は、以下のMistral AIのサイトでAPIキーを作成しましょう。
https://console.mistral.ai/api-keys

![](/images/poc-mistral-ocr/2025-03-09-00-34-29.png)

![](/images/poc-mistral-ocr/2025-03-09-00-34-41.png)

## 実装
mistralaiモジュールとipythonモジュールをインストールします。

```bash
pip install mistralai ipython
```

.envファイルに環境変数を設定します。
```bash
MISTRALAI_API_KEY="MISTRALAIのAPIキー"
```

Mistral OCRを使って、PDFファイルをMarkdown化するコードを書きます。
```python
from mistralai import Mistral, DocumentURLChunk
from pathlib import Path
import json
import os

from util.markdown_utils import get_combined_markdown

# APIキーを設定して、Mistralクライアントを作成
api_key = os.getenv("MISTRALAI_API_KEY")
client = Mistral(api_key=api_key)

# OCR対象のPDFファイル
pdf_file = Path("./Society5.0の実現に向けた科学技術・イノベーション政策 .pdf")
assert pdf_file.is_file()

# PDFファイルをアップロード
uploaded_file = client.files.upload(
    file={
        "file_name": pdf_file.stem,
        "content": pdf_file.read_bytes(),
    },
    purpose="ocr",
)

# アップロードしたファイルに対して、署名付きURLを取得
signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

# PDFファイルをOCR
pdf_response = client.ocr.process(document=DocumentURLChunk(
    document_url=signed_url.url), model="mistral-ocr-latest", include_image_base64=True)

# OCR結果を表示
response_dict = json.loads(pdf_response.model_dump_json())
json_string = json.dumps(response_dict, indent=4, ensure_ascii=False)
# OCR結果をファイルに保存。
result_file = Path("./result/ocr_result.json")
result_file.write_text(json_string, encoding="utf-8")

# Markdown形式でファイルに保存
markdown_string = get_combined_markdown(pdf_response)
markdown_file = Path("./result/ocr_result.md")
markdown_file.write_text(markdown_string, encoding="utf-8")
```

## 結果の確認

**図が含まれる文章は、以下のようにMarkdown形式に変換されています。**
PDFの上から順に処理されているようで、文章の途切れ目で図が挿入されています。もう少し、図を説明する文章が分割されずにまとまっていると良いですね。
※また、「コラム2-5」のはずが、「コラムさ-5」になってしまっていますね...
![](/images/poc-mistral-ocr/2025-03-09-00-38-55.png)


**表が含まれる文章も、以下のようにMarkdown形式に変換されています。**
表はMarkdownで表現されています。横に並んだ表であっても、二つの表として分割して認識されています。
![](/images/poc-mistral-ocr/2025-03-09-00-41-41.png)
![](/images/poc-mistral-ocr/2025-03-09-00-41-55.png)

結果の確認は以上です。

# まとめ
Mistral OCRを使って、PDFファイルをMarkdown化するPoCを行いました。
今回は、画像データはバイナリデータとしてMarkdownに埋め込まれる形になっています。生成AIへのInputとしても画像のバイナリデータを送ることができるので、活用できそうですね。

今回実装したコードはGitHubで公開しています。
https://github.com/nomhiro/poc-mistral-ocr

次は、RAGシステムへの組み込みを行っていきたいと思います。

### たまにこのようなエラーが起こりました。
同じPDFファイルで同じコードでも、5回に1回ほど以下のようなエラーになります。公開されたばかりのモデルですので、まだ安定していない可能性がありますね。今後のアップデートに期待です。
```bash
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/runpy.py", line 198, in _run_module_as_main
    return _run_code(code, main_globals, None,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/runpy.py", line 88, in _run_code
    exec(code, run_globals)
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.4.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/__main__.py", line 71, in <module>
    cli.main()
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.4.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/../debugpy/server/cli.py", line 501, in main
    run()
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.4.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/../debugpy/server/cli.py", line 351, in run_file
    runpy.run_path(target, run_name="__main__")
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.4.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 310, in run_path
    return _run_module_code(code, init_globals, run_name, pkg_name=pkg_name, script_name=fname)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.4.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 127, in _run_module_code
    _run_code(code, mod_globals, init_globals, mod_name, mod_spec, pkg_name, script_name)
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.4.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 118, in _run_code
    exec(code, run_globals)
  File "/workspaces/poc-mistral-ocr/poc-mistral-ocr.py", line 31, in <module>
    pdf_response = client.ocr.process(document=DocumentURLChunk(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/vscode/.local/lib/python3.12/site-packages/mistralai/ocr.py", line 114, in process
    raise models.SDKError(
mistralai.models.sdkerror.SDKError: API error occurred: Status 500
{"object":"error","message":"Service unavailable.","type":"internal_server_error","param":null,"code":"1000"}
```