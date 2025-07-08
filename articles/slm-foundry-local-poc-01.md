---
title: "生成AIの新たな潮流：SLM（Small Language Model）が拓く未来とLLMとの使い分け"
emoji: "🦔"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["AI", "SLM", "LLM", "Foundry"]
published: false
---

# はじめに
SLMは「Small Language Model」の名の通り、小規模な言語モデルであり、LLM（Large Language Model）と比較して、軽量で高速、低コストで動作することが特徴です。
本ブログでは、SLMの活用ケースと、Azure AI Foundry LocalをPoCします。🚀

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

# Azure AI Foundry Local を使った SLM 実行PoC

## Azure AI Foundry Localとは

https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-local/concepts/foundry-local-architecture

Azure AI Foundry Localは、デバイス（ローカル環境）上でAI推論を実行するツールです。Azureサブスクリプションを必要とせず、ローカルハードウェア上でAIモデルを直接実行できます。

このツールの主な特徴は以下の通りです：
- Azureサブスクリプション不要でジェネレーティブAIモデルをローカル実行
- すべてのデータ処理をデバイス上で実行してプライバシーとセキュリティを強化
- OpenAI互換APIを通じてアプリケーションとの統合が可能
- ONNX Runtimeとハードウェアアクセラレーションによる性能最適化

### Foundry Localのアーキテクチャ
![](/images/slm-foundry-local-poc-01/2025-07-08-22-43-17.png)

* **Foundry Local Service**: ローカルでAIモデルを実行するためのRESTサーバ含むサービス。ほかのサービスからローカルのAIモデルを実行できます。
* **ONNX Runtime**: ONNX形式のAIモデルを実行するための環境です。CPU、GPU、NPUなどハードウェアで効率的に最適化されたモデルを実行します。
* **Model Managemange**: 
  * **Model Cache**: ダウンロードしたAIモデルをデバイスにローカルに保存します。Foundry CLIやREST APIを利用できます。
  * **Lifecycle Management**: モデルのバージョン管理や更新を行います。モデルのダウンロード、ロード、実行、アンロード、削除を行います。
* **Model Compilcation(Olive)**: モデルをFoundry Localで使用する前に、ONNX形式にコンパイルして最適化するフレームワークです。これにより、モデルのサイズを小さくし、推論速度を向上させます。

### 開発者ツール
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

### 対応プラットフォームとシステム要件
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



### 注意点

* **プレビュー版の制限**
  * Foundry Localは現在パブリックプレビュー版として提供されており、機能や仕様が変更される可能性があります。本番環境での利用には注意が必要です。

* **モデルのタイムアウト**
  * モデルは一定時間（デフォルト10分）使用されないと自動的にアンロードされます。実運用では、この設定の調整が必要な場合があります。

## Foundry Local をインストールしましょう！

わたしの環境はWindowsなので、ターミナルで以下のコマンドを実行します。

```bash
winget install Microsoft.FoundryLocal
```

## SLMを実行しましょう！！

利用可能なモデルを確認します。
```bash
foundry model list
```

モデルを実行しましょう。
```bash
foundry model run phi-3.5-mini
```

このコマンドを実行すると、モデルが自動的にダウンロードされ（初回のみ）、対話型のチャットセッションが開始されます。

Foundry Localは、システムのハードウェア構成に最適なモデル種類を自動選択してくれます。
- NVIDIA GPUがある場合：CUDA最適化モデル
- Qualcomm NPUがある場合：NPU最適化モデル
- GPU/NPUがない場合：CPU最適化モデル

## Pythonアプリから実行してみましょう！！

### Python SDK
```python
import openai
from foundry_local import FoundryLocalManager

# モデルの指定（エイリアス使用）
alias = "phi-3.5-mini"

# FoundryLocalManagerインスタンスの作成
manager = FoundryLocalManager(alias)

# OpenAI Python SDKを使用してローカルモデルと対話
client = openai.OpenAI(
    base_url=manager.endpoint,
    api_key=manager.api_key
)
```

※Foundry LocalはOpenAI互換のAPIを提供するため、既存のOpenAIクライアントコードを簡単に移行できます。エンドポイントを`http://localhost:5273/v1/`に変更するだけで利用可能です。






---


# まとめ

LLMは汎用性と強力な能力でAIの可能性を広げましたが、SLMは軽量性、高速性、コスト効率、そしてデータプライバシーの面で、LLMだけではカバーできない領域を補完し、新たなAIの活用シーンを創出しています。

今後は、それぞれのモデルの特性を理解し、タスクや環境の要件に応じてLLMとSLMを適切に使い分ける「適材適所」のアプローチが、生成AIの活用を最大限に引き出す鍵となるでしょう。


Azure AI Foundry Localは、プライバシー、セキュリティ、コスト効率を重視する企業や開発者にとって有用なツールです。クラウドサービスを使わずにローカル環境でAIモデルを実行できるため、機密データの取り扱いやオフライン環境での作業が必要な場面で威力を発揮します。

簡単なインストール手順とOpenAI互換のAPIにより、既存のワークフローに容易に統合できる点も大きな魅力です。プレビュー版のため今後の機能拡張にも注目が集まります。


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