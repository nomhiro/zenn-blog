---
title: "【phi-4】Foundry LocalでSLMを実行！！～ローカルPC内完結するためにSLM活用してみよう～"
emoji: "🦔"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["AI", "SLM", "LLM", "Foundry", "phi"]
published: true
---

# はじめに
SLMは「Small Language Model」の名の通り、小規模な言語モデルであり、LLM（Large Language Model）と比較して、軽量で高速、低コストで動作することが特徴です。
本ブログでは、Foundry LocalをPoCします。🚀

※ちなみに、ローカルでSLMを実行するためのツールは、Foundry Local 以外にも、VSCodeの拡張機能「AI Toolkit」もあります。

※SLMをさらに特化型にして実用するために、Foundry LocalでFine-Tuningすることもできますが、今回はその内容は含みません。

---

# SLM（Small Language Model）とは？

### SLMの概要と特徴
**SLM（Small Language Model）**とは、その名の通り、LLMと比較してモデルのサイズが大幅に小さい言語モデルを指します。パラメータ数は数億から数十億程度と、数千億から数兆パラメータを持つLLMより小さいパラメータ数ですね。

**主な特徴**
* **軽量性:** LLMに比べて必要な計算資源が少なく、スマートフォンやIoTデバイスなどの**エッジデバイス**、あるいは一般的なPC環境でも動作可能です。
* **特化性:** 特定のドメインやタスクに特化して学習されることで、その分野において精度が高くなります。つまり、汎用性よりも専門性です。
* **高速性:** モデルサイズが小さいため、推論速度が速く、リアルタイム応答が求められるアプリケーションに適しています。
* **低コスト:** トレーニングや運用にかかるコストがLLMに比べて低く抑えられます。
* **データプライバシー:** ローカル環境やオンプレミスでの動作が可能なため、機密性の高いデータを外部に送信することなく処理でき、データプライバシー保護に優れています。
* **オフライン対応:** エッジデバイスで動作するため、インターネット接続がない環境でも動作可能です。

---

# SLMの具体的な活用事例

軽量であり、エッジデバイスで動かせる特性を活かした事例がいくつかありましたので概要を紹介します。

## JALにおけるオフライン環境での業務支援
日本航空（JAL）では、客室乗務員から空港地上スタッフへの引き継ぎレポート作成において、**オフライン環境で動作するタブレットアプリ**にMicrosoftのSLMである**Phi-4 mini**を活用しています。これにより、インターネット接続が不安定な空港の環境でも、迅速かつ正確なレポート作成を支援し、業務効率の向上とミスの削減に貢献しています。
https://news.microsoft.com/source/asia/features/jal-japanese/?lang=ja&msockid=2e027880ff1e6d6c0b756d2afe336cc4

## LLMとSLMの最適な使い分け

LLMとSLMは、それぞれ異なる強みを持つため、タスクや要件に応じて使い分けることが重要です。

### LLMが適している場面
* **汎用的な知識や常識が必要なタスク:** 幅広い分野の知識を必要とする質問応答、自由な文章生成、翻訳。
* **複雑な推論や多段階の思考を要するタスク:** 複雑な問題解決、ブレインストーミング、クリエイティブなコンテンツ生成。
* **大量の多様なデータからの要約・分析:** 広範な文書からの情報抽出、トレンド分析。
* **高性能な計算資源が利用可能で、レイテンシが許容される場合。**
* **データプライバシーの要件が比較的緩やかな場合。**

### SLMが適している場面
* **特定のドメインやタスクに特化した処理:** 特定の専門用語の理解、定型的な文章生成、分類。
* **計算資源が限られている環境:** スマートフォン、IoTデバイス、エッジコンピューティング。
* **オフライン環境での利用:** インターネット接続が不安定な場所や、セキュリティ上の理由で外部との通信が制限されている環境。
* **データプライバシーやセキュリティが最優先されるタスク:** 医療記録、金融データ、社内機密文書の処理。

---

# Azure AI Foundry Localとは

https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/concepts/foundry-local-architecture

Azure AI Foundry Localは、デバイス（ローカル環境）上でAI推論を実行するツールです。Azureサブスクリプションを必要とせず、ローカルハードウェア上でAIモデルを直接実行できます。

このツールの主な特徴は以下の通りです：
- Azureサブスクリプション不要でジェネレーティブAIモデルをローカル実行
- すべてのデータ処理をデバイス上で実行してプライバシーとセキュリティを強化
- OpenAI互換APIを通じてアプリケーションとの統合が可能
- ONNX Runtimeとハードウェアアクセラレーションによる性能最適化

## Foundry Localのアーキテクチャ
![](/images/slm-foundry-local-poc-01/2025-07-08-22-43-17.png)

* **Foundry Local Service**: ローカルでAIモデルを実行するためのRESTサーバ含むサービス。ほかのサービスからローカルのAIモデルを実行できます。
* **ONNX Runtime**: ONNX形式のAIモデルを実行するための環境です。CPU、GPU、NPUなどハードウェアで効率的に最適化されたモデルを実行します。
* **Model Managemange**: 
  * **Model Cache**: ダウンロードしたAIモデルをデバイスにローカルに保存します。Foundry CLIやREST APIを利用できます。
  * **Lifecycle Management**: モデルのバージョン管理や更新を行います。モデルのダウンロード、ロード、実行、アンロード、削除を行います。
* **Model Compilcation(Olive)**: モデルをFoundry Localで使用する前に、ONNX形式にコンパイルして最適化するフレームワークです。これにより、モデルのサイズを小さくし、推論速度を向上させます。

## 開発者ツール
- **💻 Foundry CLI**: Foundry Localのコマンドラインインターフェースで、モデルの管理や実行を行います。
  :::details Foundry CLIの例
  ```bash
  # モデル管理
  foundry model list
  foundry model run <model-name> --verbose
  foundry service status

  # キャッシュ管理
  foundry cache cd <path>
  foundry cache list
  foundry cache remove <model-name>
  ```
  :::
- **🔌 SDK Integration**: OpenAI互換のAPIなので、モデルを呼び出す側のアプリケーションは、LLMと似た方法で利用できます。
  :::details Python SDKの例
  ```python
  import openai
  from foundry_local import FoundryLocalManager

  # モデル管理とエンドポイント設定
  manager = FoundryLocalManager("phi-3.5-mini")
  client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key
  )

  # ストリーミング応答
  stream = client.chat.completions.create(
    model=manager.get_model_info("phi-3.5-mini").id,
    messages=[{"role": "user", "content": "質問内容"}],
    stream=True
  )

  for chunk in stream:
    if chunk.choices[0].delta.content:
      print(chunk.choices[0].delta.content, end="", flush=True)
  ```
  :::
- **🎨 AI Toolkit for VS Code**: Visual Studio Codeの拡張機能で、Foundry Localのモデルを管理、実行するためのツールです。
- **💬 Open WebUI**: Webブラウザのチャット画面でFoundry Localモデルとチャットできます。
  :::details セットアップ手順
  ```bash
  # Open WebUIのインストール
  pip install open-webui

  # サービス起動
  open-webui serve
  # → http://localhost:8080でアクセス可能
  ```
  :::
- **🌐 REST API**: OpenAI互換のREST APIです。RESTAPIなので、どのプログラミング言語からも簡単にアクセスできます。
  :::details REST APIの例
  ```bash
  # エンドポイント確認
  foundry service status
  # → http://localhost:5273/v1/

  # HTTPリクエスト例（curl）
  curl -X POST http://localhost:5273/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
      "model": "phi-3.5-mini",
      "messages": [{"role": "user", "content": "Hello"}]
    }'
  ```
  :::

## 対応プラットフォームとシステム要件
最新の情報はこちら
https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/get-started#prerequisites

#### 対応OS
- Windows 10 (x64)
- Windows 11 (x64/ARM)
- Windows Server 2025
- macOS

#### ハードウェア要件
**最小要件：**
- RAM：8GB
- ディスク容量：3GB以上の空き容量

**推奨要件：**
- RAM：16GB
- ディスク容量：15GB以上の空き容量

#### ハードウェアアクセラレーション（オプション）
- NVIDIA GPU（2000シリーズ以降）
- AMD GPU（6000シリーズ以降）
- Qualcomm Snapdragon X Elite（8GB以上のメモリ）
- Apple Silicon



## 注意点

* **プレビュー版の制限**
  * Foundry Localは現在パブリックプレビュー版として提供されており、機能や仕様が変更される可能性があります。本番環境での利用には注意が必要です。

* **モデルのタイムアウト**
  * モデルは一定時間（デフォルト10分）使用されないと自動的にアンロードされます。実運用では、この設定の調整が必要な場合があります。


---

# 🚀Azure AI Foundry Local を使った SLM 実行PoC

ローカルマシンのCPUは、AMD Ryzen™ AI 9 365 10 コア/20 スレッド プロセッサ ※AMD Ryzen™ AI(最大 50 NPU TOPS) です。
NPU付きのAMDですが、FoundryLocalではまだAMDのNPUは未対応です。
ですのでCPUでSLMを動かします。

## Foundry Local をインストールしましょう！

わたしの環境はWindowsなので、ターミナルで以下のコマンドを実行します。

```bash
winget install Microsoft.FoundryLocal
```
:::details 実行結果
```powershell
PoC\slm-foundry-local-poc-01 > winget install Microsoft.FoundryLocal
見つかりました Foundry Local [Microsoft.FoundryLocal] バージョン 0.4.91.9885
このアプリケーションは所有者からライセンス供与されます。
Microsoft はサードパーティのパッケージに対して責任を負わず、ライセンスも付与しません。
このパッケージには次の依存関係が必要です:
  - パッケージ
      Microsoft.VCLibs.Desktop.14 [>= 14.0.33728.0]
インストーラーハッシュが正常に検証されました
パッケージのインストールを開始しています...
  ██████████████████████████████  100%
インストールが完了しました
```
:::

## SLMを実行しましょう！！

利用可能なモデルを確認します。
```bash
foundry model list
```
:::details 実行結果
```powershell
PoC\slm-foundry-local-poc-01 > foundry model list
Alias                          Device     Task               File Size    License      Model ID
-----------------------------------------------------------------------------------------------
phi-4                          GPU        chat-completion    8.37 GB      MIT          Phi-4-generic-gpu   
                               CPU        chat-completion    10.16 GB     MIT          Phi-4-generic-cpu   
--------------------------------------------------------------------------------------------------------
mistral-7b-v0.2                GPU        chat-completion    4.07 GB      apache-2.0   mistralai-Mistral-7B-Instruct-v0-2-generic-gpu
                               CPU        chat-completion    4.07 GB      apache-2.0   mistralai-Mistral-7B-Instruct-v0-2-generic-cpu
-------------------------------------------------------------------------------------------------------------------------------------
phi-3.5-mini                   GPU        chat-completion    2.16 GB      MIT          Phi-3.5-mini-instruct-generic-gpu
                               CPU        chat-completion    2.53 GB      MIT          Phi-3.5-mini-instruct-generic-cpu
------------------------------------------------------------------------------------------------------------------------
phi-3-mini-128k                GPU        chat-completion    2.13 GB      MIT          Phi-3-mini-128k-instruct-generic-gpu
                               CPU        chat-completion    2.54 GB      MIT          Phi-3-mini-128k-instruct-generic-cpu
---------------------------------------------------------------------------------------------------------------------------
phi-3-mini-4k                  GPU        chat-completion    2.13 GB      MIT          Phi-3-mini-4k-instruct-generic-gpu
                               CPU        chat-completion    2.53 GB      MIT          Phi-3-mini-4k-instruct-generic-cpu
-------------------------------------------------------------------------------------------------------------------------
deepseek-r1-14b                GPU        chat-completion    10.27 GB     MIT          deepseek-r1-distill-qwen-14b-generic-gpu
                               CPU        chat-completion    11.51 GB     MIT          deepseek-r1-distill-qwen-14b-generic-cpu
-------------------------------------------------------------------------------------------------------------------------------
deepseek-r1-7b                 GPU        chat-completion    5.58 GB      MIT          deepseek-r1-distill-qwen-7b-generic-gpu
                               CPU        chat-completion    6.43 GB      MIT          deepseek-r1-distill-qwen-7b-generic-cpu
------------------------------------------------------------------------------------------------------------------------------
qwen2.5-0.5b                   GPU        chat-completion    0.68 GB      apache-2.0   qwen2.5-0.5b-instruct-generic-gpu
                               CPU        chat-completion    0.80 GB      apache-2.0   qwen2.5-0.5b-instruct-generic-cpu
------------------------------------------------------------------------------------------------------------------------
qwen2.5-1.5b                   GPU        chat-completion    1.51 GB      apache-2.0   qwen2.5-1.5b-instruct-generic-gpu
                               CPU        chat-completion    1.78 GB      apache-2.0   qwen2.5-1.5b-instruct-generic-cpu
------------------------------------------------------------------------------------------------------------------------
qwen2.5-coder-0.5b             GPU        chat-completion    0.52 GB      apache-2.0   qwen2.5-coder-0.5b-instruct-generic-gpu
                               CPU        chat-completion    0.80 GB      apache-2.0   qwen2.5-coder-0.5b-instruct-generic-cpu
------------------------------------------------------------------------------------------------------------------------------
qwen2.5-coder-7b               GPU        chat-completion    4.73 GB      apache-2.0   qwen2.5-coder-7b-instruct-generic-gpu
                               CPU        chat-completion    6.16 GB      apache-2.0   qwen2.5-coder-7b-instruct-generic-cpu
----------------------------------------------------------------------------------------------------------------------------
qwen2.5-coder-1.5b             GPU        chat-completion    1.25 GB      apache-2.0   qwen2.5-coder-1.5b-instruct-generic-gpu
                               CPU        chat-completion    1.78 GB      apache-2.0   qwen2.5-coder-1.5b-instruct-generic-cpu
------------------------------------------------------------------------------------------------------------------------------
phi-4-mini                     GPU        chat-completion    3.72 GB      MIT          Phi-4-mini-instruct-generic-gpu
                               CPU        chat-completion    4.80 GB      MIT          Phi-4-mini-instruct-generic-cpu
----------------------------------------------------------------------------------------------------------------------
phi-4-mini-reasoning           GPU        chat-completion    3.15 GB      MIT          Phi-4-mini-reasoning-generic-gpu
                               CPU        chat-completion    4.52 GB      MIT          Phi-4-mini-reasoning-generic-cpu
-----------------------------------------------------------------------------------------------------------------------
qwen2.5-14b                    CPU        chat-completion    11.06 GB     apache-2.0   qwen2.5-14b-instruct-generic-cpu
-----------------------------------------------------------------------------------------------------------------------
qwen2.5-7b                     GPU        chat-completion    5.20 GB      apache-2.0   qwen2.5-7b-instruct-generic-gpu
                               CPU        chat-completion    6.16 GB      apache-2.0   qwen2.5-7b-instruct-generic-cpu
----------------------------------------------------------------------------------------------------------------------
qwen2.5-coder-14b              GPU        chat-completion    8.79 GB      apache-2.0   qwen2.5-coder-14b-instruct-generic-gpu
                               CPU        chat-completion    11.06 GB     apache-2.0   qwen2.5-coder-14b-instruct-generic-cpu
```
:::

モデルを実行しましょう。
```bash
foundry model run phi-4-mini
```

:::details 実行結果
```powershell
PoC\slm-foundry-local-poc-01 > foundry model run phi-4-mini
Downloading Phi-4-mini-instruct-generic-cpu...
[####################################] 100.00 % [Time remaining: about 0s]        34.5 MB/s
🕗 Loading model... 
🟢 Model Phi-4-mini-instruct-generic-cpu loaded successfully

Interactive Chat. Enter /? or /help for help.

Interactive mode, please enter your prompt
> 
```
:::

このコマンドを実行すると、モデルが自動的にダウンロードされ（初回のみ）、対話型のチャットセッションが開始されます。

Foundry Localは、システムのハードウェア構成に最適なモデル種類を自動選択してくれます。
- NVIDIA GPUがある場合：CUDA最適化モデル
- Qualcomm NPUがある場合：NPU最適化モデル
- GPU/NPUがない場合：CPU最適化モデル

## Pythonアプリから実行してみましょう！！

Python の openai モジュールを使います。ローカルモデルをopenaiモジュールで利用するために、FoundryLocalManagerを使ってエンドポイントとAPIキーを設定します。
※Foundry LocalはOpenAI互換のAPIを提供するため、既存のOpenAIクライアントコードを簡単に移行できます。エンドポイントを`http://localhost:5273/v1/`に変更するだけで利用可能です。

```python
import openai
from foundry_local import FoundryLocalManager

def main():

    # モデルの指定（エイリアス使用）
    alias = "phi-4-mini"

    # FoundryLocalManagerインスタンスの作成
    manager = FoundryLocalManager(alias)

    # OpenAI Python SDKを使用してローカルモデルに接続
    client = openai.OpenAI(
        base_url=manager.endpoint,
        api_key=manager.api_key
    )

    # 回答生成
    response = client.chat.completions.create(
        model=manager.get_model_info(alias).id,
        messages=[{"role": "user", "content": "こんにちは！phi-4-miniモデルが動きましたね！"}]
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()

```

もちろん、Streaming APIもサポートしています。
```python
import openai
from foundry_local import FoundryLocalManager

def main():

    # モデルの指定（エイリアス使用）
    alias = "phi-4-mini"

    # FoundryLocalManagerインスタンスの作成
    manager = FoundryLocalManager(alias)

    # OpenAI Python SDKを使用してローカルモデルに接続
    client = openai.OpenAI(
        base_url=manager.endpoint,
        api_key=manager.api_key
    )

    # ストリームで回答生成
    stream = client.chat.completions.create(
        model=manager.get_model_info(alias).id,
        messages=[{"role": "user", "content": "こんにちは！phi-4-miniモデルが動きましたね！"}],
        stream=True
    )
    for chunk in stream:
        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # 改行


if __name__ == "__main__":
    main()
```

## REST APIからも実行してみましょう！！
```python
import requests
import json

def main():
    url = "http://localhost:5273/v1/chat/completions"  # REST APIのエンドポイント
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": "Phi-4-mini-instruct-generic-cpu",
        "messages": [
            {"role": "user", "content": "こんにちは"}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "stop": None,
        "max_tokens": 1000,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "logit_bias": {},
        "user": "run-slm-restapi",
        "functions": [],
        "function_call": None,
        "metadata": {}
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        data = response.json()
        # assistantのメッセージのみ出力
        try:
            print(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError):
            print("Unexpected response format:", data)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()
```

大量の「こんにちは」が返ってきました。。。GPT3.5あたりのLLMモデルを思い出します...
```powershell
(slm-openai-sdk) 20_slm\slm-foundry-local-poc-01 > uv run .\run-slm-restapi.py
こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこ んにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにち はこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこん にちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちは こんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんにちはこんに ちはこんにちはこんにちは
```

パラメータをいじりながら試してみましたが、frequency_penaltyの値が影響しているようでした。
frequency_penaltyの範囲は -2.0 から 2.0 です。 値が大きいと、テキスト内の頻度に基づいてトークンをペナルティが重くなり、繰り返しをしづらくなります。
frequency_penaltyを1にすると、まともな回答が返ってきました。
```python
        "frequency_penalty": 1,
```

```powershell
(slm-openai-sdk) 20_slm\slm-foundry-local-poc-01 > uv run .\run-slm-restapi.py
こんにちは！今日はどのようにお手伝いできますか？
```


## Open Web UI を使ってみましょう！！
チャットUIベースでローカルモデルの動作確認するにはOpen Web UIです。

Python3.11の環境が必要です。
```powershell
uv init poc-open-webui -p 3.11
cd poc-open-webui
```

インストールします。
```powershell
uv add open-webui
```

起動します。
```powershell
.\.venv\Scripts\activate
open-webui serve
```

:::details 実行結果
```powershell
(poc-open-webui) 20_slm\poc-open-webui > open-webui serve 
Loading WEBUI_SECRET_KEY from file, not provided as an environment variable.
Generating a new secret key and saving it to C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.webui_secret_key
Loading WEBUI_SECRET_KEY from C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.webui_secret_key
C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.venv\Lib\site-packages\open_webui
C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.venv\Lib\site-packages
C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.venv\Lib
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 7e5b5dc7342b, init
INFO  [alembic.runtime.migration] Running upgrade 7e5b5dc7342b -> ca81bd47c050, Add config table
INFO  [alembic.runtime.migration] Running upgrade ca81bd47c050 -> c0fbf31ca0db, Update file table
INFO  [alembic.runtime.migration] Running upgrade c0fbf31ca0db -> 6a39f3d8e55c, Add knowledge table
Creating knowledge table
Migrating data from document table to knowledge table
INFO  [alembic.runtime.migration] Running upgrade 6a39f3d8e55c -> 242a2047eae0, Update chat table
Converting 'chat' column to JSON
Renaming 'chat' column to 'old_chat'
Adding new 'chat' column of type JSON
Dropping 'old_chat' column
INFO  [alembic.runtime.migration] Running upgrade 242a2047eae0 -> 1af9b942657b, Migrate tags
INFO  [alembic.runtime.migration] Running upgrade 1af9b942657b -> 3ab32c4b8f59, Update tags
Primary Key: {'name': None, 'constrained_columns': []}
Unique Constraints: [{'name': 'uq_id_user_id', 'column_names': ['id', 'user_id']}]
Indexes: [{'name': 'tag_id', 'column_names': ['id'], 'unique': 1, 'dialect_options': {}}]
Creating new primary key with 'id' and 'user_id'.
Dropping unique constraint: uq_id_user_id
Dropping unique index: tag_id
INFO  [alembic.runtime.migration] Running upgrade 3ab32c4b8f59 -> c69f45358db4, Add folder table
INFO  [alembic.runtime.migration] Running upgrade c69f45358db4 -> c29facfe716b, Update file table path
INFO  [alembic.runtime.migration] Running upgrade c29facfe716b -> af906e964978, Add feedback table
INFO  [alembic.runtime.migration] Running upgrade af906e964978 -> 4ace53fd72c8, Update folder table and change DateTime to BigInteger for timestamp fields
INFO  [alembic.runtime.migration] Running upgrade 4ace53fd72c8 -> 922e7a387820, Add group table
INFO  [alembic.runtime.migration] Running upgrade 922e7a387820 -> 57c599a3cb57, Add channel table
INFO  [alembic.runtime.migration] Running upgrade 57c599a3cb57 -> 7826ab40b532, Update file table
INFO  [alembic.runtime.migration] Running upgrade 7826ab40b532 -> 3781e22d8b01, Update message & channel tables
INFO  [alembic.runtime.migration] Running upgrade 3781e22d8b01 -> 9f0c9cd09105, Add note table
WARNI [open_webui.env] 

WARNING: CORS_ALLOW_ORIGIN IS SET TO '*' - NOT RECOMMENDED FOR PRODUCTION DEPLOYMENTS.

INFO  [open_webui.env] Embedding model set: sentence-transformers/all-MiniLM-L6-v2
C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.venv\Lib\site-packages\pydub\utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
  warn("Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work", RuntimeWarning)
ERROR [chromadb.telemetry.product.posthog] Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
WARNI [langchain_community.utils.user_agent] USER_AGENT environment variable not set, consider setting it to identify your requests.

 ██████╗ ██████╗ ███████╗███╗   ██╗    ██╗    ██╗███████╗██████╗ ██╗   ██╗██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██║    ██║██╔════╝██╔══██╗██║   ██║██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║ █╗ ██║█████╗  ██████╔╝██║   ██║██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ██║███╗██║██╔══╝  ██╔══██╗██║   ██║██║
╚██████╔╝██║     ███████╗██║ ╚████║    ╚███╔███╔╝███████╗██████╔╝╚██████╔╝██║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝     ╚══╝╚══╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝


v0.6.15 - building the best AI user interface.

https://github.com/open-webui/open-webui

Fetching 30 files:   0%|                                                                            | 0/30 [00:00<?, ?it/s]Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
config.json: 100%|████████████████████████████████████████████████████████████████████████████████| 190/190 [00:00<?, ?B/s]
C:\Users\nom40\Documents\PoC\20_slm\poc-open-webui\.venv\Lib\site-packages\huggingface_hub\file_download.py:143: UserWarning: `huggingface_hub` cache-system uses symlinks by default to efficiently store duplicated files but your machine does not support them in C:\Users\nom40\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2. Caching files will still work but in a degraded version that might require more space on your disk. This warning can be disabled by setting the `HF_HUB_DISABLE_SYMLINKS_WARNING` environment variable. For more details, see https://huggingface.co/docs/huggingface_hub/how-to-cache#limitations.
To support symlinks on Windows, you either need to activate Developer Mode or to run Python as an administrator. In order to activate developer mode, see this article: https://docs.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development
  warnings.warn(message)
modules.json: 100%|███████████████████████████████████████████████████████████████████████████████| 349/349 [00:00<?, ?B/s]
data_config.json: 39.3kB [00:00, 39.1MB/s]                                                       | 0.00/349 [00:00<?, ?B/s] 
README.md: 10.5kB [00:00, 18.4MB/s]s]
.gitattributes: 1.23kB [00:00, ?B/s]
Fetching 30 files:   3%|██▎                                                                 | 1/30 [00:00<00:07,  4.05it/s]Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
config.json: 100%|████████████████████████████████████████████████████████████████████████████████| 612/612 [00:00<?, ?B/s]
config_sentence_transformers.json: 100%|██████████████████████████████████████████████████████████| 116/116 [00:00<?, ?B/s]
config_sentence_transformers.json:   0%|                                                         | 0.00/116 [00:00<?, ?B/s]Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`M [00:00<?, ?B/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
model.safetensors: 100%|██████████████████████████████████████████████████████████████| 90.9M/90.9M [00:02<00:00, 32.8MB/s]
model_qint8_arm64.onnx: 100%|█████████████████████████████████████████████████████████| 23.0M/23.0M [00:04<00:00, 5.03MB/s]
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`00:12, 5.52MB/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`████████████                                                     | 21.0M/90.4M [00:04<00:13, 5.21MB/s] 
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`00:29, 2.67MB/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
model_qint8_arm64.onnx: 100%|█████████████████████████████████████████████████████████| 23.0M/23.0M [00:01<00:00, 14.8MB/s]
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`00:08, 6.61MB/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`████████████████████                                             | 31.5M/90.4M [00:05<00:09, 6.14MB/s]
model_O4.onnx: 100%|██████████████████████████████████████████████████████████████████| 45.2M/45.2M [00:07<00:00, 6.30MB/s]
model_O1.onnx:  23%|███████████████▎                                                  | 21.0M/90.4M [00:05<00:16, 4.20MB/s]Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
openvino_model.xml: 211kB [00:00, 140MB/s]
openvino_model.xml: 0.00B [00:00, ?B/s]███▉                                           | 31.5M/90.4M [00:06<00:11, 5.15MB/s]Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`<00:08, 5.81MB/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
model_qint8_arm64.onnx: 100%|█████████████████████████████████████████████████████████| 23.0M/23.0M [00:02<00:00, 8.74MB/s]
openvino_model_qint8_quantized.xml: 368kB [00:00, 368MB/s]████████████████████████████| 23.0M/23.0M [00:02<00:00, 8.85MB/s]
model_quint8_avx2.onnx: 100%|█████████████████████████████████████████████████████████| 23.0M/23.0M [00:04<00:00, 4.89MB/s]
model_O3.onnx:  58%|██████████████████████████████████████▎                           | 52.4M/90.3M [00:10<00:07, 4.83MB/s]Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`<00:09, 4.90MB/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`x: 100%|█████████████████████████████████████████████████████████| 23.0M/23.0M [00:04<00:00, 5.00MB/s]
                                                                                                                           Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
openvino_model_qint8_quantized.bin: 100%|█████████████████████████████████████████████| 22.9M/22.9M [00:03<00:00, 6.40MB/s]
sentence_bert_config.json: 100%|████████████████████████████████████████████████████████| 53.0/53.0 [00:00<00:00, 35.2kB/s]
special_tokens_map.json: 100%|████████████████████████████████████████████████████████████████████| 112/112 [00:00<?, ?B/s]
                                                                                                                           Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`<00:05, 4.95MB/s]
WARNI [huggingface_hub.file_download] Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`████████████████████████████████████████████▉                    | 62.9M/90.4M [00:11<00:04, 6.66MB/s]
model_O1.onnx: 100%|██████████████████████████████████████████████████████████████████| 90.4M/90.4M [00:13<00:00, 6.50MB/s]
openvino_model.bin: 100%|█████████████████████████████████████████████████████████████| 90.3M/90.3M [00:07<00:00, 12.1MB/s]
tokenizer.json: 466kB [00:00, 15.5MB/s]
tokenizer_config.json: 100%|██████████████████████████████████████████████████████████████████████| 350/350 [00:00<?, ?B/s]
train_script.py: 13.2kB [00:00, ?B/s]█████████████████████████████████████▌           | 73.4M/90.3M [00:06<00:01, 11.9MB/s]
vocab.txt: 232kB [00:00, 4.75MB/s]█▏                                                  | 21.0M/90.9M [00:04<00:14, 4.81MB/s]
pytorch_model.bin: 100%|██████████████████████████████████████████████████████████████| 90.9M/90.9M [00:06<00:00, 14.2MB/s]
model.onnx: 100%|█████████████████████████████████████████████████████████████████████| 90.4M/90.4M [00:17<00:00, 5.14MB/s]
model_O2.onnx: 100%|██████████████████████████████████████████████████████████████████| 90.3M/90.3M [00:18<00:00, 4.97MB/s]
model_O3.onnx: 100%|██████████████████████████████████████████████████████████████████| 90.3M/90.3M [00:18<00:00, 4.92MB/s] 
tf_model.h5: 100%|████████████████████████████████████████████████████████████████████| 91.0M/91.0M [00:07<00:00, 13.0MB/s]
rust_model.ot: 100%|██████████████████████████████████████████████████████████████████| 90.9M/90.9M [00:09<00:00, 9.85MB/s]
Fetching 30 files: 100%|███████████████████████████████████████████████████████████████████| 30/30 [00:20<00:00,  1.43it/s]
INFO:     Started server process [7160]
INFO:     Waiting for application startup.                                            | 31.5M/91.0M [00:04<00:07, 7.79MB/s]
2025-07-13 23:47:20.126 | INFO     | open_webui.utils.logger:start_logger:140 - GLOBAL_LOG_LEVEL: INFO - {}
2025-07-13 23:47:20.126 | INFO     | open_webui.main:lifespan:514 - Installing external dependencies of functions and tools... - {}
2025-07-13 23:47:20.132 | INFO     | open_webui.utils.plugin:install_frontmatter_requirements:241 - No requirements found in frontmatter. - {}
```
:::

Open WebUI サーバーが起動し、http://localhost:8080 からアクセスできます

こんな感じの初期画面が表示されます。
![](/images/slm-foundry-local-poc-01/2025-07-13-23-52-39.png)

管理者アカウントを作成します。
![](/images/slm-foundry-local-poc-01/2025-07-14-08-07-33.png)

ローカルモデルと接続設定を行います。
右上のアカウントアイコンから「設定」画面を開きます。
![](/images/slm-foundry-local-poc-01/2025-07-14-08-10-38.png)

「接続」タブから「直接接続」を「＋」します。
FoundryCLIでURLを確認します。※Port番号が動的に変わる可能性があるためです。
```powershell
foundry service status
```

「接続を追加」画面で Foundry CLI で 確認したPortで、http://localhost:<Port>/v1/ を入力します。
キーは任意の値を設定します。※testなど
![](/images/slm-foundry-local-poc-01/2025-07-14-08-15-17.png)

保存します。
![](/images/slm-foundry-local-poc-01/2025-07-14-08-16-10.png)

それでは、これで準備完了です。
チャット画面でモデルを選択し、ローカルモデルとチャットしましょう！
![](/images/slm-foundry-local-poc-01/2025-07-14-08-17-46.png)


## phi-4-mini と phi-4 Output比較
phi-4-miniは、モデルサイズが4GB程度ですが、phi-4は10GB程度です。出力の差を確認してみましょう。


- 質問1：こんにちは
  - phi-4-mini
    ```text
    こんにちは！今日はどのようにお手伝いできますか？
    ```
  - phi-4
    ```text
    こんにちは！はい、phi-4-miniモデルは動作しました。このモデルは、量子場理論における相互 作用を研究するために使用されるシンプルな理論モデルです。特に、スカラー場の相互作用を扱 う際に、量子力学的な振る舞いを理解するための基本的なツールとして利用されます。このモデ ルは、量子場理論の基本的な概念を学ぶための良い出発点となります。何か具体的な質問や興味 があることがあれば、お気軽にどう |
    ```
- 質問2：AはBより背が高く、CはAより背が低い。DはCより背が高いがBより背が低い。この4人を身長順に並べてください
  - phi-4-mini
    不正解ですね。
    :::details phi-4-miniの回答
    ```text
    与えられた情報に基づいて、身長順を決定しましょう:

    1. AはBより背が高い。
    2. CはAより背が低い。
    3. DはCより背が高いがBより背が低い。

    これらの情報を使って、身長順を見つけることができます:

    - CはAより背が低いので、Cは最も背が低いです。
    - DはCより背が高いので、DはCより背が高いです。
    - AはBより背が高いので、AはBより背が高いです。
    - DはBより背が低いので、DはBより背が低いです。

    これらの情報を組み合わせると、BはDより背が低いので、BはCより背が低いです。したがって、Bは最も背が低いです。        

    身長順は次の通りです:

    B < D < A < C

    ただし、CはAより背が低いので、CはAよりも背が高いです。したがって、正しい身長順は次の通りです:

    B < D < C < A

    これが4人の身長順です。
    ```
    :::
  - phi-4
    ```text
    (slm-openai-sdk) 20_slm\slm-foundry-local-poc-01 > uv run .\run-slm-sdk.py
    与えられた情報を整理してみましょう：

    1. AはBより背が高い。
    2. CはAより背が低い。
    3. DはCより背が高いが、Bより背が低い。

    これらの情報から、次のように身長の順序を導き出せます：

    - A > B（AはBより背が高い）
    - A > C（CはAより背が低い）
    - D > C（DはCより背が高い）
    - B > D（DはBより背が低い）

    これらの情報を基に、身長の順序を考えます：

    1. AはBより背が高く、Cよりも背が高いので、Aは最も背が高いです。
    2. BはAより背が低いですが、Dより背が高いので、Bは次に背が高いです。
    3. DはCより背が高いですが、Bより背が低いので、Dは次に背が高いです。
    4. CはAより背が低く、Dよりも背が低いので、Cは最も背が低いです。

    したがって、身長順に並べると次のようになります：

    A > B > D > C
    ```
- 質問：
    システムメッセージ
  ```text
  与えられる長文を読んで、3つの異なる視点（技術者向け、経営者向け、一般消費者向け）でそれぞれ100字以内で要約してください
  絶対に日本語で回答してください。
  ```
  ユーザメッセージ
  ```text
  日本では過去10年にわたり、自動運転技術の研究開発と社会実装に向けた動きが本格化してきた。特に政府の主導による政策、法整備、支援インフラの整備は、実用段階へと進む大きな後押しとなっている。この記事では、自動運転に関する政府の戦略と現在の取り組み状況について、時系列で詳しく振り返りつつ、今後の展望を述べていく。

  開発初期の官民連携によるロードマップ（2014〜2020年）
  2014年度から始まった「官民ITS構想・ロードマップ」では、自動運転を国家戦略と位置づけ、毎年内容を更新しながら、技術開発や法制度の整備が進められた。目標としては「2030年までに世界一安全で円滑な道路交通社会の実現」「2020年までに世界最先端のITSの構築」などが掲げられ、法整備面では2020年の改正道路交通法によりレベル3自動運転が可能となり、さらに2023年にはレベル4の運行を「特定自動運行」として規定する法律も施行された。

  この期間において、自家用車分野ではホンダが2020年に世界初のレベル3型式指定車「LEGEND」を発表。移動サービス分野では、秋田県や福井県永平寺町で限定地域にてレベル4相当の運行が実現された。また、物流サービスに関しては、高速道路上でのトラック隊列走行技術の確立と、無人後続車の実証実験が成功を収めている。

  モビリティ・ロードマップと岸田政権の展望（2023年〜）
  2023年以降、政府は新たな指針として「モビリティ・ロードマップ」を策定し、実証段階から事業化への移行を目指すフェーズへと政策の方向性を変更した。ロードマップでは、2024年度に技術の習熟化と制度の透明性向上を図り、2025〜2026年度には導入コストの低減と人材育成を推進。2027年度以降には制度の普及とモビリティ市場の確立を目指している。

  岸田政権下では、デジタル田園都市構想に基づき「無人自動運転移動サービスを2025年度までに50カ所、2027年度までに100カ所以上で展開する」という具体的な目標も定められた。これに対応する形で、MaaSやAIオンデマンド交通、キャッシュレス導入といった施策も並行して進められている。

  自動運転支援道とインフラ整備
  インフラ面でも「自動運転支援道」が構想され、2024年度には新東名高速道路において優先レーンが設置される計画が進行中。これにより、路側インフラからの情報提供やデータ連携基盤の整備が行われ、安全で円滑な自動運転トラックの運行を支援することが可能となる。また、地方都市でもLiDARやカメラを使ったインフラ連携が検討されており、都市部と地方を問わず支援体制が強化されている。

  自動運転の現状と展望（2025年1月時点）
  2025年初頭時点で、国土交通省が展開する補助金制度には99の地方自治体が採択され、自動運転の地域実装が加速。民間企業ではBOLDLYやティアフォーなどが先導し、レベル4運行可能な地域が二桁に到達しようとしている。

  一方で自家用車分野におけるレベル3やレベル4の動向は停滞傾向にあり、現在はADAS（先進運転支援システム）レベル2＋の高度化が中心となっている。
  ```
  - phi-4-mini
  　要約はされていますが、技術者/経営者/一般消費者向けの視点がいまいちですね。
    ```text
    技術者向け要約:
    自動運転技術は、政府主導のロードマップにより、技術開発と法制度の整備が進められています。レベル3自動運転は2020年に可能となり、レベル4運行は2023年に規定されました。モビリティ・ロードマップでは、技術習熟化と制度透明性の向上が目標とされ、デジタル田園都市構想に基づき無人自動運転サービスの展開が計画されています。

    経営者向け要約:
    日本政府は、モビリティ・ロードマップを通じて自動運転技術の事業化を目指しています。2024年から導入コストの低減と人材 育成を推進し、2027年以降はモビリティ市場の確立を目指しています。自動運転支援道の整備やインフラ整備も進められており 、地方自治体も自動運転の地域実装を加速しています。

    一般消費者向け要約:
    日本では、自動運転技術が進歩しており、レベル3自動運転は2020年から可能になりました。モビリティ・ロードマップでは、技術の習熟化と制度の透明性向上を目指しています。無人自動運転サービスの展開やインフラ整備が進められており、将来的には 自動運転が日常生活でより一般的になることが期待されています。
    ```
  - phi-4
    phi-4-miniと比べて、技術者/経営者/一般消費者向けの視点が分かれています。
    ```text
    ### 技術者向けの要約
    日本では、政府主導で自動運転技術の研究開発が進み、2020年にはレベル3自動運転が可能となり、2023年にはレベル4の「特定 自動運行」が法制化された。ホンダのレベル3車両や無人トラックの実証実験が成功し、2024年には自動運転支援道の整備が進む。技術の習熟化と制度の透明性向上が2024年度の目標である。

    ### 経営者向けの要約
    日本政府は自動運転技術の実用化を推進し、2020年にはレベル3自動運転が可能となり、2023年にはレベル4の法制化が行われた 。ホンダや民間企業が先導し、2025年までに無人自動運転移動サービスを50カ所以上で展開する計画がある。自動運転支援道の 整備やMaaSの推進が経営戦略に影響を与える。

    ### 一般消費者向けの要約
    日本では自動運転技術が急速に進化し、2020年にはレベル3自動運転が可能となり、2023年にはレベル4の法制化が行われた。ホ ンダがレベル3車両を発表し、無人トラックの実証実験も成功。2025年までに無人自動運転サービスが50カ所以上で利用可能になる予定で、自動運転支援道の整備も進む。
    ```

# 🚀週次報告書を作成してみよう
シーンとして、オフライン環境もしくはインターネット接続が不安定な環境で、日々の議事録から週次報告書を作成することを想定します。
フォルダには、「20250708-14」のような形式で、日付を含むフォルダがあり、その中に会議体や案件でフォルダ分けされながら議事録のテキストファイルが格納されているとします。
![](/images/slm-foundry-local-poc-01/2025-07-14-10-49-53.png)

Pythonを使って、以下のような処理を行います。
1. 指定したローカルフォルダから、今日の日付を含むフォルダを検索します。
2. フォルダ内の全てのテキストファイルを読み込み
3. 読み込んだ内容を1つの文字列にまとめます。（ユーザメッセージとなる）
4. Foundry LocalのSLMモデルを使って、週次報告書を生成します。
5. 生成された週次報告書を出力します。

```python
import openai
from foundry_local import FoundryLocalManager
import os
import glob
from datetime import datetime

# 変数で指定するローカルフォルダパス
BASE_DIR = r"C:\Users\nom40\Documents\PoC\20_slm\slm-foundry-local-poc-01\サンプル議事録"  # 必要に応じて変更

# 今日の日付を取得し、YYYYMMDD形式で格納
TODAY = datetime.now().strftime("%Y%m%d")

# フォルダ名に今日の日付が含まれるものを検索（例: 20250708-14）

# フォルダ名（例: 20250708-14）が今日を含む週かどうかを判定
from datetime import timedelta

def is_today_in_range(folder_name, today):
    # 例: 20250708-14
    try:
        if '-' not in folder_name:
            return False
        start_str, end_str = folder_name.split('-')
        # start_str: 20250708, end_str: 14
        start_date = datetime.strptime(start_str, "%Y%m%d")
        # end_strが日だけの場合、start_dateの月・年を使う
        end_date = datetime.strptime(start_str[:6] + end_str, "%Y%m%d")
        today_date = datetime.strptime(today, "%Y%m%d")
        return start_date <= today_date <= end_date
    except Exception:
        return False

def find_today_folder(base_dir, today):
    for name in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, name)) and is_today_in_range(name, today):
            return os.path.join(base_dir, name)
    return None

def collect_all_text_files(folder):
    # サブディレクトリも含めてテキストファイル（.txt, .md）を再帰的に取得
    files = glob.glob(os.path.join(folder, '**', '*.txt'), recursive=True)
    files += glob.glob(os.path.join(folder, '**', '*.md'), recursive=True)
    contents = []
    for file in files:
        with open(file, encoding='utf-8') as f:
            contents.append(f"# {os.path.relpath(file, folder)}\n" + f.read())
    return '\n\n'.join(contents)

def main():
    alias = "phi-4"
    manager = FoundryLocalManager(alias)
    client = openai.OpenAI(
        base_url=manager.endpoint,
        api_key=manager.api_key
    )

    today_folder = find_today_folder(BASE_DIR, TODAY)
    if not today_folder:
        print(f"本日({TODAY})を含むフォルダが見つかりませんでした。")
        return

    all_notes = collect_all_text_files(today_folder)
    if not all_notes:
        print("本日の議事録ファイルが見つかりませんでした。")
        return

    system_message = """
あなたは優秀なAIアシスタントです。与えられた1週間分の会議メモや作業メモをもとに、週次報告資料をMarkdown形式で作成してください。重要なトピック、進捗、課題、次週の予定などを分かりやすくまとめてください。
上位報告向けの週次資料です。各案件の状況が分かるように報告資料にしてください。
必ず日本語で出力してください。
"""

    user_message = f"""
以下は今週の議事録・作業メモです。これをもとに週次報告資料をMarkdownで作成してください。

{all_notes}
"""


    response = client.chat.completions.create(
        model=manager.get_model_info(alias).id,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}],
        max_tokens=4096,
    )
    report_content = response.choices[0].message.content
    print(report_content)

    # 出力をreports/weekly_report/日付.mdに保存
    output_dir = os.path.join(os.path.dirname(__file__), "reports", "weekly_report")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{TODAY}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"週次報告を {output_path} に保存しました。")

if __name__ == "__main__":
    main()
```

このように作成してくれました。
```markdown
# プロダクト開発チーム週次報告書

**報告期間:** 2025年07月08日 - 2025年07月15日

## エグゼクティブサマリー

今週は、WorkPulseプロジェクトのSprint1の初日から終了までの進捗を報告します。Desktop Agentのデータ送信機能が完成し、Web FrontendとWeb Backend間の初期連携が成功しました。来週は、これらの機能をさらに洗練させ、本番環境への準備を進める予定です。

---

## 今週の主要成果

### 開発進捗
- **完了した機能・タスク**
  - Desktop Agent: キーボード・マウスイベントのデータ構造確定とBackendへのデータ送信機能実装
  - Web Frontend: ダッシュボードの主要コンポーネントの初期実装
  - Web Backend: データ受信APIのモックアップ完成とFirestoreへのデータ保存ロジック実装
  - インフラ: App ServiceとFirestoreのプロビジョニング完了とAzure Monitorの初期設定

### リリース・デプロイ状況
- **本番環境:** なし
- **ステージング環境:** データ送信機能のテスト中
- **次回リリース予定:** 2025年07月22日

---

## 課題・リスク

### 🔴 クリティカル
- **課題:** データ送信頻度とBackendでの処理能力の調整
- **影響:** データの遅延や損失
- **対応策:** 10秒に1回程度のバッチ送信を想定し、調整を進める
- **期限:** 2025年07月12日

### 🟡 注意が必要
- **課題:** Backendからのデータ取得方法の選定
- **対応策:** Fetch APIまたはAxiosの利用を検討

---

## チーム状況

### 人員状況
- **稼働可能メンバー:** 5名/5名
- **新規参加:** なし
- **休暇・不在:** なし

### スキル・リソース
- **技術的課題:** データ送信頻度の最適化、エラーハンドリングの検討
- **外部リソース:** なし

---

## 来週の計画

### 優先度高
1. **機能開発:** ダッシュボードのデータ表示機能の強化
2. **品質向上:** データ送信機能のエラーハンドリングとロギングの実装
3. **リリース準備:** ステージング環境での全体テストと最適化

### 重要なマイルストーン
- **07月16日:** ダッシュボードのデータ表示機能の初期実装
- **07月18日:** データ送信機能のエラーハンドリングとロギングの実装

---

## 上位への要望・相談事項

### 意思決定が必要な事項
- **事項1:** データ送信頻度の最適化に関する意思決定
- **事項2:** Backendからのデータ取得方法の最終決定

### リソース要請
- **人員:** なし
- **予算:** なし
- **技術支援:** なし

---

**次回報告予定:** 2025年07月22日
```

ローカル端末のスペック次第でphiモデルの応答スピードがかなり変わりますし、NPUなどあったとしてリアルタイム性は厳しいです。
ただ、バックエンド処理で裏で勝手にレポートしてくれるなどの用途であれば問題ないですね。


# まとめ

SLMは軽量性、高速性、コスト効率、そしてデータプライバシーの面で、エッジデバイス側の処理という観点で新たなAIの活用シーンがありそうです。
タスクや環境の要件に応じてLLMとSLMを適切に使い分ける「適材適所」のアプローチがありそうです。

Azure AI Foundry Localは、プライバシー、セキュリティ、コスト効率を重視する企業や開発者にとって有用なツールです。クラウドサービスを使わずにローカル環境でAIモデルを実行できるため、機密データの取り扱いやオフライン環境での作業が必要な場面で活用できます。

# 参考情報

### 使いそうなコマンドライン
* サービス状態確認
```bash
foundry service status
```

* 詳細ログ出力
```bash
foundry model run <model> --verbose
```

* キャッシュの確認と修復
```bash
foundry cache list
foundry cache cd ./foundry/cache/models
```

* HuggingFace認証確認
```bash
huggingface-cli whoami
```