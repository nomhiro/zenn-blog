---
title: "【Foundry続編】Hosted Agent が GA！MAF エージェントを azd で載せる PoC ハンズオン"
emoji: "📦"
type: "tech"
topics: ["azure", "microsoftfoundry", "aiエージェント", "agent", "hostedagent"]
published: false
---

![Microsoft Foundry の Hosted Agents を中心にした、エージェント基盤の全体像](/images/foundry-hosted-agent-ga-maf-agui/2026-07-18-15-21-16.png)
*Microsoft が示すエージェント基盤の全体像。本記事はこの中心にある「Run」を扱います*

**任意のフレームワーク・任意の言語・任意のモデル**で作ったエージェントに、Microsoft Foundry が「エージェント向けのネイティブコンピュート」を提供します。これが今回 **GA** になった Hosted Agent の肝です。

GitHub Copilot App で**構築**し、Microsoft IQ で**組織の知識に接続**し、Foundry で**実行**します。さらに Microsoft Teams と**安全に連携**し、Agent 365 で**ガバナンス**し、ログ収集 → 学習 → チューニング → 分析の**ループを回して改善していく**。個々のツールを寄せ集めるのではなく、この一連の流れが**ひとつの基盤の上でつながっている**のがポイントです。

> 本記事では、その中心にある **Run**（Hosted Agent）に焦点を当て、[前回記事（2026年2月時点）](https://zenn.dev/nomhiro/articles/microsoft-foundry-hosted-agent)からの差分を整理します。そのうえで、MAF（Microsoft Agent Framework）で作った予約アシスタント（推論＋ツール呼び出し）を、**そのまま Hosted Agent に載せる** PoC をハンズオンでやってみます。

📖
https://azure.microsoft.com/en-us/blog/frontier-models-and-production-agents-advancing-microsoft-foundry-for-the-agentic-era/
https://x.com/jeffhollan

:::message
本記事は 2026年7月時点 の情報に基づいています。Microsoft Foundry は進化が速いため、最新情報は必ず公式ドキュメントを参照してください。
:::

## TL;DR

- Microsoft Foundry の **Hosted Agent が一般提供**（GA）になりました（2026年7月）。GPT-5.6 の GA・アジア太平洋データゾーンと同時の発表です。
- ただし「GAで初めて来た機能」と「5月のプレビュー・リフレッシュで来た機能」は別物。根本的なアーキテクチャ刷新（レプリカ方式 → セッションサンドボックス方式）は**5月時点で完了**しています。GAではそこに本番SLA・回復性のあるタスク（プライベートプレビュー）などが乗った、という関係です。
- ハンズオンでは、MAF で作った予約アシスタント（推論 → 在庫検索・見積ツールの呼び出し）を Hosted Agent に載せます。エントリポイントは **`InvocationsHostServer` に `Agent` を渡すだけの約10行**。`azd up` 一発、実測3分でクラウドのエージェントエンドポイントが立ちました。
- とはいえ GA 直後らしいハマりどころもありました。**手書き `azure.yaml` に必須の `infra: provider: microsoft.foundry`**、**`env:` ではなく `environmentVariables:`**（map 形式ではなく list 形式）、**ロール改名**（`Azure AI User` → `Foundry User`）と **identity が2つある問題**。全部実測ログ付きで書きます。
- セッション状態の維持（`--session-id` の追撃ターンで文脈が引き継がれる）、未使用時ゼロ課金、専用 Entra ID、OpenTelemetry トレースまで、Hosted Agent のうれしさを一通り体験できる構成です。

---

## はじめに

GAとなり、「前回ローカルで作った MAF のエージェントを、Hosted Agent に載せよ～」と思い、試してみることにしました。

前回ローカルで作った MAF エージェントの記事はこちらです。
https://zenn.dev/nomhiro/articles/maf-ag-ui-generative-ui-poc

📖
https://azure.microsoft.com/en-us/blog/frontier-models-and-production-agents-advancing-microsoft-foundry-for-the-agentic-era/
https://x.com/jeffhollan
https://x.com/satyanadella
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents

---

## Hosted Agent とは（前回のおさらい）

Hosted Agent は、**自分で書いたエージェントのコードをコンテナ化し、Microsoft のマネージドインフラ上でエージェントとして実行する仕組み**です。

前回記事で触れたとおり、Foundry のエージェントには2系統あります。

| 種類 | 定義方法 | ランタイム |
| --- | --- | --- |
| プロンプトベースエージェント | ポータルでプロンプト＋ツールを構成 | Foundry がフルマネージドで実行 |
| **Hosted Agent** | 自分のコードをコンテナイメージ化 | Foundry がマネージドで実行（本記事の主役） |

公式が挙げる「プロンプトベースより Hosted Agent を選ぶべき」ケースは次の4つです。

- **自分のコードを持ち込みたい**：Agent Framework / LangGraph / Semantic Kernel / 独自コードなど、プロンプトだけでは表現できないロジックを書きたい。
- **カスタムプロトコルを使いたい**：Webhook や非 OpenAI 形式のペイロードを受けたい。
- **コンピュートを制御したい**：サンドボックスの CPU / メモリを指定したい。
- **ステートフルなワークロードを動かしたい**：`$HOME` と `/files` でターンをまたいで状態を保持したい。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/overview
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents

---

## Hosted Agent の何がうれしいのか

「エージェントのロジックは書けた。でも本番に載せる部分が地獄」。コンテナ化、Webサーバ、ID、状態永続化、スケーリング、可観測性。こういう面倒ごとをまるごと肩代わりしてくれるのが Hosted Agent です。整理するとこんな感じです。

### Any framework / Any language / Any model

- **任意のフレームワーク**：Microsoft Agent Framework、LangGraph、OpenAI Agents SDK、Claude Agent SDK、GitHub Copilot SDK、独自コード。
- **任意の言語**：Python / C#。
- **任意のモデル**：OpenAI / Anthropic / Meta / Mistral / MAI など Foundry モデルカタログから選択。

**特定のハーネスやモデルにロックインされない** というのがいいですね。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents
https://devblogs.microsoft.com/foundry/introducing-the-new-hosted-agents-in-foundry-agent-service-secure-scalable-compute-built-for-agents/

### セッション単位の VM 分離サンドボックス（本モデルの目玉）

各セッションが**専用のファイルシステムを持つ VM レベル分離のサンドボックス**で動きます。単なるプロセス分離やコード実行コンテナではなく、ハイパーバイザレベルの分離です。

これがなぜ重要かというと、**任意のコードを実行するエージェント**（コーディングエージェント等）では、ユーザーAのセッションでユーザーBのデータを覗けてしまう事故が致命的だからです。セッションごとにサンドボックスが分かれることで、任意コード実行でもクロスセッションのデータ漏洩が起きません。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents
https://devblogs.microsoft.com/foundry/introducing-the-new-hosted-agents-in-foundry-agent-service-secure-scalable-compute-built-for-agents/
https://www.neowin.net/news/microsoft-launches-hosted-agents-in-foundry-with-secure-sandboxes/
https://ankitbko.github.io/blog/2026/05/hosted-agents-part-1/

使っていない時間はコンピュートも課金もゼロな仕組みなのも、クラウドならではのサーバーレス的なメリットです。

- レプリカ数もウォームプールも設定不要。**セッション単位**でスケール。
- アイドル時はコンピュートが解放され、**動いていない時間は課金されない**。
- コールドスタートにかかる時間は読みやすく、再開時にはセッションの状態（`$HOME` / `/files`）が復元される。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents

### 状態の永続化

- `$HOME` と `/files` の内容が、ターン間・アイドル期間をまたいで保持される（アイドル15分でコンピュート解放、状態は保持。30日で完全削除）。
- 会話履歴は Foundry 側に保存され、ポータル / API / Teams など**チャネルをまたいで同じ会話にアクセス**できる。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents

### 専用 ID とエンドポイントの自動発行

- デプロイ時に**専用の Microsoft Entra ID**（エージェントID）と**専用エンドポイント**を Foundry が自動で作ってくれる。マネージドIDやルーティングの手動構成は不要。
- ユーザー対話時は OAuth 2.0 OBO（On-Behalf-Of）で「ユーザーの代理」として下流を呼べる。無人時はエージェントID自身で認証。
- 前回の[ツール認証記事](https://zenn.dev/nomhiro/articles/microsoft-foundry-tool-auth)で扱った「開発中はProject共有ID、公開後はAgent固有ID」の設計がここにつながる。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/agent-identity

### 組み込みの可観測性・バージョニング・ネットワーク

- **可観測性**：Application Insights の接続文字列を自動で注入してくれて、OpenTelemetry トレースが既定で出る。
- **バージョニング**：不変のエージェントバージョン＋重み付け配信で、カナリア/ブルーグリーンデプロイが可能。
- **ネットワーク**：ネットワーク分離リソース内でのデプロイ、VNet 送信、プライベート ACR（2026/6/25以降作成のプロジェクト）に対応。

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents
https://learn.microsoft.com/en-us/azure/foundry/concepts/general-availability

### 本番SLA（GAで追加）

GAに伴い、SLA・エンタープライズサポート付きで本番運用に使える扱いになりました。SLAの具体値は公式ページで要確認です。

📖
https://azure.microsoft.com/en-us/blog/frontier-models-and-production-agents-advancing-microsoft-foundry-for-the-agentic-era/
https://azure.microsoft.com/pricing/details/foundry-agent-service/

---

## PoC のお題：MAF のエージェントを Hosted Agent に載せる

### M365 Copilot でよくない？

プロンプトエージェントや M365 Copilot で足りるなら、わざわざ Hosted Agent を使う理由はありません。だから PoC のシナリオは、**それらでは書けないこと**を選ぶべきです。Hosted Agent だけの差別化ポイントは主に4つ。

- **独自ハーネス / フレームワーク**：Microsoft Agent Framework（MAF）/ LangGraph / Claude Agent SDK など、プロンプト定義では書けない**エージェンティックなロジック**（推論ループ・ツール・状態）をコードごと持ち込める。
- **カスタムプロトコル**：OpenAI 非互換の任意ペイロードを受けられる（→ **Invocations プロトコル**）。
- **任意コードの隔離実行**：ユーザーごとに microVM で分離。
- **長時間・自律実行**：状態を保ったまま長く走り続ける。

今回突くのは1つ目、独自ハーネス（MAF）で書いたエージェントを、**コードごとマネージドランタイムに持ち込む**体験です。プロンプト定義に翻訳するのではなく、推論ループもツールもそのまま運ぶ。ここが、ポータルで完結するプロンプトエージェントと決定的に違うところです。

### シナリオ

> 別記事で、ローカルに [MAF の「しろくまレンタカー予約アシスタント」](https://zenn.dev/nomhiro/articles/maf-ag-ui-generative-ui-poc) を作りました。ユーザーの曖昧な要望（「5月に札幌で家族4人」）から、エージェントが**推論**し、在庫検索・空き確認・見積の**ツール**を自分で選んで呼び、候補を提案する、という MAF らしい振る舞いをします。
>
> 本記事では、**このエージェントを Foundry の Hosted Agent に載せて本番ランタイム化**します。ツール群（在庫検索・空き確認・見積）はローカル版の実装をそのまま import し、足すのは Hosted Agent 用のエントリポイント1ファイルだけです。

### プロトコルの選択

Hosted Agent は複数のプロトコルを選べます。会話エージェントならまず勧められているのは OpenAI 互換の **Responses**（会話履歴の管理までプラットフォームがやってくれる）。今回は独自ペイロード（`{"message": "..."}` のシンプルな JSON）で受けたいので、任意ペイロードを素通しできる **Invocations** を使います。Invocations では、プラットフォームはペイロードの中身をまったく解釈しません。これが実際どういうことかは、あとで Playground を触るとよく分かります。

:::message
トレードオフ：Invocations は自由度が高い代わりに、Teams / M365 Copilot への自動ブリッジ（Activity）や A2A は**使えません**。会話系で Teams 配信も欲しいなら Responses を選ぶことになります。
:::

### この1シナリオで踏む主要機能

ハンズオンで、右列のエビデンスを各ステップに貼っていきます。

| 機能・メリット | このPoCでの体験の仕方 | エビデンス |
| --- | --- | --- |
| **独自ハーネス MAF の持ち込み** ★差別化 | MAF の `Agent`（推論＋ツール）をそのまま載せる | エントリポイント実装・Dockerfile |
| **Invocations**（任意ペイロード）★差別化 | `{"message"}` の独自 JSON ワイヤで対話 | `azd ai agent invoke` / Playground の挙動 |
| セッション & 会話状態 | 予約コンテキストをターンをまたいで保持 | `--session-id` 指定の追撃ターン |
| 専用 Entra ID | エージェントIDでモデル呼び出し（キーレス） | ロール割り当てと認証まわりの実録 |
| 未使用時はゼロに縮む | 対話の合間にアイドル → 再開 | ウォーム/コールドのレイテンシ |
| セッション分離 | セッションIDごとに別サンドボックス | `sessions list` の確認 |
| 可観測性 | 推論・ツール呼び出しのトレース | `azd ai agent monitor`（OTel スパン） |

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents
https://learn.microsoft.com/en-us/agent-framework/hosting/foundry-hosted-agent
https://zenn.dev/nomhiro/articles/maf-ag-ui-generative-ui-poc

---

## 各構成要素の補足

冒頭の全体像で示した各要素を、もう少し具体的に補足します。Hosted Agent は単体で見るより、**この一連の流れの一部として見たほうが**良さが分かりやすいです。

- **Build**（GitHub Copilot App / 任意フレームワーク）：好きな環境で構築。Dockerfile で OS 依存や必要なツールまで含めて定義できる。
- **Ground**（Microsoft IQ）：Work IQ / Fabric IQ / Foundry IQ で企業データに接地（グラウンディング）。
- **Run**（Foundry Hosted Agent）：本記事の主役。マネージドなランタイム・スケーリング・専用ID・可観測性を提供。
- **Reach**（Microsoft Teams / M365 Copilot）：Activity ブリッジで業務チャネルへ安全に配信。
- **Govern**（Agent 365）：組織全体のエージェントをガバナンス。
- **Improve**（ログ収集 → 学習/ナレッジ化 → チューニング/改善 → 分析/インサイト のループ）：Agent Optimizer などで学びを積み上げて、次のバージョンへ反映していく。

以降は、中心の **Run**（Hosted Agent）に絞って掘り下げます。

📖
https://azure.microsoft.com/en-us/blog/frontier-models-and-production-agents-advancing-microsoft-foundry-for-the-agentic-era/
https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-build-2026/

---

## 前回記事（2026/2）からの差分

前回記事は **リフレッシュ前**（レプリカ方式）がベースでした。現在は **セッションサンドボックス方式** に全面刷新されています。

| 観点 | 前回記事（旧・レプリカ方式） | 現在（新・セッションサンドボックス方式） |
| --- | --- | --- |
| デプロイ手段 | `az cognitiveservices agent start/stop/update` | Dockerfileで環境定義し `azd deploy`。SDK / VS Code Toolkit 経路も |
| スケーリング | `--min-replicas` / `--max-replicas` | レプリカ廃止。**セッション単位**でスケール（設定不要） |
| 分離モデル | 明示的な言及薄い | 各セッションが**VMレベル分離のサンドボックス** |
| 状態管理 | なし | **セッション**（`$HOME`/`/files`）と**会話**（Foundry保存）の2層 |
| プロトコル | Responses 中心 | Responses / Invocations / Invocations（WS）/ Activity / A2A |
| ツール接続 | エージェントに直接付与 | **Toolbox の MCP エンドポイント経由**（直接付与は非対応） |
| ID | Entra 配下に発行 | デプロイ時に**専用 Entra ID + 専用エンドポイント**を自動作成 |
| サンドボックスサイズ | なし | 0.5 / 1 / 2 vCPU（1 / 2 / 4 GiB） |
| リージョン | 限定的 | 東日本含む20リージョン |
| フレームワーク | Agent Framework（Python） | 任意（MAF / LangGraph / OpenAI / Claude / Copilot SDK …） |
| バージョニング | なし | 不変バージョン＋重み付け配信（カナリア/ブルーグリーン） |
| ネットワーク | なし | VNet 送信 / プライベート ACR（2026/6/25以降作成） |
| 関連機能 | なし | Memory・Toolbox・Routines・Agent Optimizer・Voice Live |
| 土台 | なし | Microsoft Agent Framework 1.0 が GA（2026/4/2） |
| 名称 | Azure AI Foundry / Azure AI User ロール | **Microsoft Foundry** / **Foundry User** 等へ改名 |

:::message
名称変更に注意：`Azure AI Foundry` → `Microsoft Foundry`、URLも `ai-foundry` → `foundry`。RBACロールも `Azure AI User/Owner…` → `Foundry User/Owner…` に改名されています（IDと権限は不変）。ハンズオンで実際にこの改名にハマったので、後述します。
:::

📖
https://devblogs.microsoft.com/foundry/introducing-the-new-hosted-agents-in-foundry-agent-service-secure-scalable-compute-built-for-agents/
https://devblogs.microsoft.com/foundry/hosted-agents-build26/
https://learn.microsoft.com/ja-jp/azure/foundry/agents/quickstarts/quickstart-hosted-agent
https://learn.microsoft.com/ja-jp/azure/foundry/agents/concepts/hosted-agents
https://devblogs.microsoft.com/foundry/from-local-to-production-the-complete-developer-journey-for-building-composing-and-deploying-ai-agents/
https://learn.microsoft.com/en-us/azure/foundry/concepts/general-availability

---

## ハンズオン：PoC を動かす

さて、ここからが本題です。先ほどのシナリオ（MAF の予約アシスタント）を **Hosted Agent 化**していきます。

流れは「`azure.yaml` を書く → エントリポイントを約10行書く → `azd up`」の3つだけ。ただし GA 直後らしいハマりどころがいくつかあったので、それも実測ログ付きで共有します。

:::message
前提バージョン：`azd` 1.28.0 ／ `azure.ai.agents` extension 1.0.0-beta.5 ／ Python 3.12。モデルは gpt-5.4-mini（GlobalStandard）。リージョンは東日本（japaneast）。ローカルの MAF エージェント（前回記事の予約アシスタント）が手元にある前提です。
:::

📖
https://learn.microsoft.com/ja-jp/azure/foundry/agents/quickstarts/quickstart-hosted-agent
https://learn.microsoft.com/en-us/agent-framework/hosting/foundry-hosted-agent
https://learn.microsoft.com/ja-jp/azure/foundry/agents/how-to/deploy-hosted-agent
https://learn.microsoft.com/ja-jp/azure/foundry/agents/how-to/manage-hosted-agent
https://zenn.dev/nomhiro/articles/maf-ag-ui-generative-ui-poc

### 🔧 Step 0: セットアップ

`azd` と Hosted Agent 用の extension を入れます。

```bash
azd extension install azure.ai.agents
azd auth login
```

インストール状態はこうなります（実行時点のバージョン）。

```text
$ azd version
azd version 1.28.0 (commit 8eb1a107…) (stable)

$ azd extension list --installed
ID                     NAME                             STATUS          INSTALLED      SOURCE
azure.ai.agents        Foundry agents (Beta)            Up to date      1.0.0-beta.5   azd
azure.ai.projects      Foundry Projects (Beta)          Up to date      1.0.0-beta.2   azd
microsoft.foundry      Microsoft Foundry (Beta)         Up to date      1.0.0-beta.1   azd
…
```

※ `azure.ai.agents` を入れると `azd ai agent …` コマンド群が使えるようになります。

### 📄 Step 1: azure.yaml を書く（手書き派の必須ポイントあり）

公式クイックスタートは `azd ai agent init` でサンプルから初期化する流れですが、今回は既存リポジトリに後付けするので **azure.yaml を手書き**しました。これがこんな感じです。

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/Azure/azure-dev/main/schemas/v1.0/azure.yaml.json
requiredVersions:
    extensions:
        azure.ai.agents: '>=1.0.0-beta.4'
name: shirokuma-hosted-agent
services:
    ai-project:
        host: azure.ai.project
        deployments:
            - model:
                format: OpenAI
                name: gpt-5.4-mini
                version: "2026-03-17"
              name: gpt-5.4-mini
              sku:
                capacity: 10
                name: GlobalStandard
    shirokuma-reservation:
        project: .
        host: azure.ai.agent      # ← Hosted Agent
        language: docker
        uses:
            - ai-project
        container:
            resources:
                cpu: "1"
                memory: 2Gi        # ← サンドボックスサイズ指定
        environmentVariables:      # ← list 形式（後述の罠）
            - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
              value: ${AZURE_AI_MODEL_DEPLOYMENT_NAME}
        kind: hosted
        protocols:
            - protocol: invocations   # ← 任意ペイロードを受ける Invocations
              version: 2.0.0
infra:
    provider: microsoft.foundry    # ← ★手書き派はこの1行が必須
```

手書きで2回ハマったので、先に共有しておきます。

1. **`infra: provider: microsoft.foundry` が Bicep-less の正体**。ドキュメントは「`azd ai agent init` は Bicep-less がデフォルト」と言いますが、その配線はこの末尾の1行です（公式サンプルを漁って発見）。これが無いと azd は標準 Bicep プロバイダにフォールバックし、`infra/main.bicep が無い` エラーと Docker `imgId` エラーで**二重に失敗**します。
2. **エージェントの env は `environmentVariables:`**（list形式）。azd 本体のスキーマにある `env:`（map形式）は extension に**無視されます**。コンテナ内で `AZURE_AI_MODEL_DEPLOYMENT_NAME` が未設定になり、readiness 到達前にクラッシュして `session_not_ready` (424) が返ってくるだけなので、原因特定に苦労しました。

Dockerfile はシンプルです。Hosted Agent のコンテナが満たすべき要件（linux/amd64・ポート8088・`GET /readiness`・`POST /invocations`）は後述の adapter が満たしてくれるので、イメージは「依存を入れてエントリポイントを起動するだけ」です。

```dockerfile
FROM --platform=linux/amd64 python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/app/.venv PORT=8088
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY src ./src
RUN uv sync --frozen --no-dev
EXPOSE 8088
CMD ["uv", "run", "--no-dev", "python", "-m", "shirokuma_rental.hosted_maf"]
```

※ `FOUNDRY_PROJECT_ENDPOINT` / `AZURE_AI_MODEL_DEPLOYMENT_NAME` / `APPLICATIONINSIGHTS_CONNECTION_STRING` はランタイムでプラットフォームが注入してくれます。`.env` をイメージに焼かないよう `.dockerignore` で除外しておきます。

### 🚀 Step 2: エントリポイントは約10行。`InvocationsHostServer` で載せる

Agent Framework のホスティング統合（`agent-framework-foundry-hosting`）を使うと、MAF の `Agent` を渡すだけで Invocations サーバが立ちます。エントリポイントはこれだけです。

```python
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import InvocationsHostServer
from azure.identity import DefaultAzureCredential

from .tools import check_availability, estimate_price, list_stores, search_cars

client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],   # プラットフォームが注入
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=DefaultAzureCredential(),                        # エージェントのマネージドID
)

agent = Agent(
    name="ShirokumaReservationAssistant",
    instructions=INSTRUCTIONS,
    client=client,
    tools=[search_cars, list_stores, check_availability, estimate_price],
)

server = InvocationsHostServer(agent)

if __name__ == "__main__":
    server.run()
```

「**MAFで実装したエージェントが約10行で丸ごと本番ランタイムに載る**」ことが何よりの良さですね。

ワイヤは `InvocationsHostServer` が規定していて、リクエストが `{"message": "...", "stream": bool}`、レスポンスが `{"response": "...", "session_id": "..."}`（`stream: true` ならテキストの SSE）です。エージェント側で規定するプロトコルなので、クライアントはこの形を知っている必要があります。ここが「プラットフォームは中身を解釈しない」Invocations らしいところで、後で Playground の挙動にも表れます。

:::message
さらに自由度が欲しい場合（独自のイベントストリームや非テキストのペイロードを流したい場合）は、`InvocationsHostServer` の土台になっている低レベル adapter `azure-ai-agentserver-invocations`（`InvocationAgentServerHost`）を直接使い、`@app.invoke_handler` で HTTP リクエスト/レスポンスを完全に自分で握ることもできます。この場合も、ランタイムとの約束事の面倒はそのまま adapter が見てくれます。
:::

デプロイして動作を見てみます。

```bash
azd up   # provision + deploy（今回の実測：約3分で完了）
```

リソースグループに Foundry アカウント・プロジェクト・ACR・gpt-5.4-mini のモデルデプロイメントが作成され、エージェントエンドポイントが発行されます。

![azd up の実行結果。約3分で provision + deploy が完了し、エージェントエンドポイントが発行される](/images/foundry-hosted-agent-azd-up.png)
*azd up 一発で Foundry アカウント / プロジェクト / ACR / モデルデプロイメント / Hosted Agent まで作成される（実測 2分52秒）*

Foundry ポータルにもエージェントが現れます。ここで Invocations らしい挙動が1つ。Playground のチャットタブは**任意ペイロードの応答を描画できません**（プラットフォームはペイロードの型を知らないので当然です）。入力欄に `{"message": "..."}` の JSON を打つと、エージェントは 200 で応答しますが吹き出しには出ません。代わりに右の**ログストリーム**に OpenTelemetry のスパン（`invoke_agent` → `chat gpt-5.4-mini` → `execute_tool search_cars` …）が流れるので、そこで動作確認する形になります。

![Foundry ポータルの Playground。チャットタブに JSON を入力した状態。応答は吹き出しに描画されず、右ペインのログストリームに OpenTelemetry スパンが流れている](/images/foundry-hosted-agent-portal-playground.png)
*invocations は pass-through なので Playground チャットは応答を描画できない。動作はログストリーム（OTel スパン）で確認する*

「エージェントを呼び出す」タブはクライアントのサンプルコードを生成してくれます。よく見ると `credential.get_token("https://ai.azure.com/.default")` とあります。エージェントエンドポイントやプロジェクト配下の OpenAI 互換面を自前クライアントで呼ぶときは、トークンの audience が `cognitiveservices` ではなく **`https://ai.azure.com`** であることに注意が必要です（間違えると 401。実測で確認しました）。

![「エージェントを呼び出す」タブに表示された Python サンプルコード。get_token の scope が https://ai.azure.com/.default になっている](/images/foundry-hosted-agent-portal-invoke-sample.png)
*ポータル生成のサンプルコード。エンドポイントの audience が `https://ai.azure.com` であることが読み取れる（10行目）*

`azd ai agent invoke` で呼んでみると、こんな感じで動きます。

```bash
azd ai agent invoke shirokuma-reservation '{"message": "7人乗りで北海道を回りたい"}'
# → 車種候補の日本語応答が返る

azd ai agent invoke shirokuma-reservation --session-id <前回のsession_id> \
  '{"message": "7人乗りのSUVだと3日間で？"}'
# → 前ターンの文脈（日程）を引き継いで 43,500円 の見積を返す
```

**`--session-id` を指定した追撃ターンで文脈が維持される**こと、ウォームセッションの応答が **2.4秒** だったことを確認しました。会話履歴を自前で持ち回らなくても、セッションがコンテキストを覚えてくれています。

![azd ai agent invoke の実行結果。1ターン目で車種候補を提案し、--session-id を付けた2ターン目では前ターンの日程を記憶したまま見積を返す](/images/foundry-hosted-agent-invoke.png)
*1ターン目（コールドスタート 12.8秒）と、同一セッションの2ターン目（ウォーム 2.4秒）。「7人乗りのSUV」「3日間」が前ターンの文脈から解決されている*

### 🔑 Step 3: ハマりどころ。ロールと「2つの identity」

デプロイ直後、エージェントからのモデル呼び出しが 401 `PermissionDenied` で落ちました。ここが今回いちばん時間を溶かしたところなので、詳しめに書きます。

1. **ロールは自動割り当てされない**。`azd up` はインフラとデプロイまでで、エージェントの identity にモデル呼び出し権限は付きません。
2. **ロール名が変わっている**。ドキュメントの言う `Azure AI User` ロールは、現テナントでは **`Foundry User`** に改名済みでした（GUID `53ca6127-db72-4b80-b1b0-d745d6d5456d` は同一。公式も rename ロールアウト中と明記）。ポータルで `Azure AI User` を探しても見つからず、しばらく混乱しました。なお `Cognitive Services OpenAI User` だけでは不十分です（プロジェクト data plane のチェックで弾かれる）。
3. **identity は2つあり、両方に要る**。`azd ai agent show` が出す **Instance Identity** と **Blueprint Principal** は別物で、セッションコンテナはどちらのトークンも使い得ます。Instance 側だけにロールを付けたところ、**セッション単位で成功/失敗が固着**する不思議な状態になりました（コンテナがトークンをキャッシュするため）。実測では 4/5 のセッションが成功し、1/5 が失敗のまま固着。Blueprint Principal にも同じ `Foundry User` を割り当てると、固着していたセッションも成功に転じました。

ロール伝播には数分かかり、成功と失敗が混在する期間があります。「さっき成功したのにまた401」となっても慌てず、少し待つのが正解です。

![azd ai agent show の出力。Instance Identity Principal ID と Blueprint Principal ID の2つの identity が表示されており、その両方に Foundry User ロールを割り当てるコマンドを示している](/images/foundry-hosted-agent-show-identity.png)
*`azd ai agent show` に出る **Instance Identity** と **Blueprint Principal** は別物。両方に `Foundry User` を割り当てて初めて全セッションが安定する*

### 📊 Step 4: 運用まわり（ログ・セッション・可観測性）

運用系のコマンドはこのあたりを常用しました。

```bash
azd ai agent show shirokuma-reservation                        # ステータス・エンドポイント・identity
azd ai agent sessions list shirokuma-reservation               # セッション一覧
azd ai agent monitor shirokuma-reservation --session-id <id>   # コンテナログをストリーム
```

`session_not_ready` (424) のようなエラーは、`monitor --session-id` でコンテナログを見るのが最短です（前述の env 未設定クラッシュもこれで特定しました）。

可観測性について、実際に動かして分かったことを1つ補足します。ドキュメント上は `APPLICATIONINSIGHTS_CONNECTION_STRING` がランタイム注入されることになっていますが、今回の Bicep-less 構成（`infra: provider: microsoft.foundry`）で作られたのは Foundry アカウント・プロジェクト・ACR の3つだけで、**Application Insights は作成されませんでした**。

それでも adapter の OpenTelemetry 計装は生きていて、推論・ツール呼び出しのスパンが**コンテナの stdout に出力される**ため、`monitor` 経由でトレースを追えます。Application Insights で Transaction search を使いたい場合は、リソースを自分で作って接続文字列をエージェントの `environmentVariables` に渡す一手間が必要そうです（このあたりも GA 直後らしいところ）。

![azd ai agent monitor でセッションコンテナのログをストリームし、環境変数未設定によるコンテナ起動時クラッシュ（RuntimeError）を特定している画面](/images/foundry-hosted-agent-monitor.png)
*`session_not_ready` (424) の正体はコンテナ起動時のクラッシュだった。`monitor --session-id` でコンテナの stderr がそのまま見えるので、原因特定が一気に楽になる*

---

## まとめ

- Hosted Agent は **GA**。ただし「刷新（5月）」と「GA（7月）」で来た機能は別物なので、分けて覚えておくと混乱しません。
- メリットの核は **任意フレームワーク/言語/モデル × セッション分離 × 未使用時ゼロ課金 × 専用ID × 組み込み可観測性**。本番化の「配管」をまるごと肩代わりしてくれます。
- 載せる作業は「`azure.yaml` を書く → `InvocationsHostServer` に `Agent` を渡す約10行のエントリポイント → `azd up`」だけ。めちゃめちゃ楽ですね。
- Invocations は pass-through です。プラットフォームはペイロードを解釈しない（Playground のチャットが応答を描画できないのはその裏返し）ので、**ワイヤの主導権は開発者側**にあります。会話系で Teams 配信までやるなら Responses を選ぶ、という使い分けです。
- 一方で実運用では、手書き `azure.yaml` の罠（`infra: provider: microsoft.foundry` / `environmentVariables:` の list 形式）、ロール改名（`Azure AI User` → `Foundry User`）、「identity が2つある」問題など、ドキュメントの先を行くハマりどころもまだあります。このあたりは GA 直後らしさですね。

個人的には、「ローカルで検証したツール実装をそのまま import して、クラウドのセッションサンドボックスに載せ替えられた」ことが想像以上に気持ちよかったです。ハーネスを自分で選べる本番ランタイム、という Hosted Agent の立ち位置がよく分かる PoC になりました。次は Teams 配信（Responses / Activity 経路）や resilient task support あたりを試してみたいと思います。

## 関連記事（自分の過去記事）

前回記事（プロンプトベース）
https://zenn.dev/nomhiro/articles/microsoft-foundry-agent-poc-20260125

前回記事（Hosted Agent）
https://zenn.dev/nomhiro/articles/microsoft-foundry-hosted-agent

前回記事（ツール認証）
https://zenn.dev/nomhiro/articles/microsoft-foundry-tool-auth

本PoCの予約アシスタントを作った記事（MAF）
https://zenn.dev/nomhiro/articles/maf-ag-ui-generative-ui-poc
