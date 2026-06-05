---
title: "Azure Functions Skills で AzureFunctions上で動くエージェント をAI駆動開発する！"
emoji: "🐻‍❄️"
type: "tech"
topics: ["azure", "azurefunctions", "githubcopilot", "ai", "mcp"]
published: false
---

## はじめに

Microsoft Build 2026、今年もたくさんアップデートがありますねー。その中の、**Azure Functions Skills** と、**Serverless Agent Runtime** について触れてみます。

まず Azure Functions Skills（`@azure/functions-skills`）です。Build 2026 で公開された npm 製のプラグインで、GitHub Copilot CLI / Claude Code / Codex CLI みたいなコーディングエージェントに、Azure Functions 固有の判断知識（どのトリガーを使うか、どの設定が非推奨か、デプロイ前に何を見ておくか …）を教え込んでくれます。

https://github.com/azure/azure-functions-skills

もう一方が、Azure Functions の **Serverless Agent Runtime** です。`.agent.md` でエージェントを定義したら、あとは普通の Functions アプリとしてデプロイするだけ、という仕組みです（実行は Microsoft Agent Framework が担います）。

https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-serverless-agents-runtime

この記事では、この2つを使って AI エージェントを実際に作っていきます。ひとつのユースケースに絞って、Copilot CLI ＋ Skills の AI 駆動開発で、作って運用するところまで通しでやってみます。

---

## 作る題材

題材は架空の車関連事業です。「顧客のプロフィールが更新された」というシステム的なイベントをきっかけに、その人に合いそうな車種を先回りで提案してくれるエージェントを作ってみます。

- 起動：`event_grid_trigger`（プロフィール更新／契約更新接近イベント。ペイロードに `customer_id`）
- 処理：保有車履歴・家族構成からニーズを推論 → カタログ照会ツールで裏取り → おすすめを複数、理由つきで生成
- 出力：最終応答のみ（通知・送信はしない＝副作用なし）

全体像はこんな構成です。イベントを起点に、エージェントが**ツールで裏取り（接地）**しながらおすすめを返すまでが一枚で見えます。

![車種提案エージェントの構成図](/images/poc-azure-functions-skills/architecture.png)

### なぜ Azure Functions ？

Functions の特徴を踏まえると、向いているのはこういうワークロードです。

> 不定期に飛んでくるイベントに即応し、待機中はゼロにスケールする

顧客イベントっていつ来るか分からないし、来たらすぐ処理したい。とくに既存システムからのイベントを処理したい場合に向いています。
チャット的なエージェントであれば、Microsoft Foundry の Agent Service を使いましょう。

---

## Azure Functions Skills の概要

`install`（や `plugin install`）すると、プラグインの実体が `~/.copilot/installed-plugins/azure-functions-skills/…`（GitHub だと [`templates/skills/`](https://github.com/Azure/azure-functions-skills) 配下）に展開されます。中を覗くと、Functions の**作成から運用まで**を一通りカバーするスキル群が入っていました。まずは「何が用意されていて、どんな構造なのか」を押さえておきます。

### 用意されているスキル

実測（`0.0.4-preview`）で **11 個**のスキルが入っていました（対応エージェントは GitHubCopilot / claudeCode / codex）。

| スキル | 役割 |
| --- | --- |
| `azure-functions-setup` | 前提（Azure CLI / Core Tools / 言語ランタイム）の確認・導入案内 |
| `azure-functions-create` | 新規 Functions プロジェクトのスキャフォールド |
| `azure-functions-agents` | Functions 上で動く AI エージェント（サーバーレスエージェント）の構築・デプロイ |
| `azure-functions-deploy` | デプロイ（Azure Skills の prepare → validate → deploy へ委譲するプロキシ） |
| `azure-functions-best-practices` | 本番レディネスレビュー（承認ゲート付きの是正提案） |
| `azure-functions-diagnostics` | デプロイ／ランタイム／トリガー／ログの障害調査 |
| `azure-functions-health-status` | 稼働状態・メトリクス・テレメトリの取得 |
| `azure-functions-inventory` | 構成インベントリ（SKU・ランタイム・設定・関数/トリガー一覧）の収集 |
| `azure-functions-doctor` | デプロイ前のローカル検査（決定論チェック＋意味解析） |
| `azure-functions-feedback` | 気づきを Issue/PR の下書きに |
| `azure-functions-common` | 言語・バインディングの共有リファレンス（他スキルが内部で参照） |

最後の `azure-functions-common` は単体で呼ぶというより、他スキルが引く"共有知識"です。そして `install` を使うと、これらを意図に応じて振り分ける**ルーティングエージェント `functions-copilot`** も `.github/agents/` に置かれます（今回は plugin だけなので置いていません）。

### スキル1つの構造

スキルはどれも1つのディレクトリで、だいたいこんな構成です。

```text
skills/<skill-name>/
├─ SKILL.md          # YAML フロントマター（name / description / argument-hint）＋ 本文
├─ references/*.md   # 知識を分割した md（必要な分だけ読む＝Progressive Disclosure の実体）
├─ scripts/*.ps1     # 決定論的に Azure を叩く収集スクリプト（health-status / inventory）
└─ assets/           # 雛形一式（agents は quickstart サンプルを同梱）
```

`SKILL.md` 自体は、YAML フロントマター（`name` / `description` / `argument-hint`）＋本文という構成で、本文には「**やりたいこと（Need）→ 読むべき `references`**」の対応が書かれています。この `description`（いつ呼ばれるか）と、必要な参照だけを開く仕組みが効きどころです。どう呼ばれて、どう知識を小出しにするのかは、次章でもう少し整理します。

---

## Azure での AI エージェントについて

ここからは少し話が変わり、Azure 上で動く AI エージェントについて説明します。今回開発する対象のエージェントでもあります。
Microsoft Build 2026 でいくつもエージェントに関連するアップデートがあり、混乱を生みそうなので整理しておきます。

- 本記事で作るもの＝Azure Functions の「Serverless Agent Runtime」。`.agent.md`（markdown）でエージェントを定義し、普通の Functions アプリとしてデプロイします。実行は Microsoft Agent Framework が担います。
- Foundry の "Hosted Agents" は別物。Foundry Agent Service 上で動くコンテナ型のエージェントです。

### Serverless Agent Runtimeについて

今回は、一つ目のほうの「Serverless Agent Runtime」を使います。

https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-serverless-agents-runtime

Functions のエージェントは、`.agent.md` で定義されたエージェントを、Microsoft Agent Framework が Functions 上で動かす、という仕組みです。Functions Skills は、このエージェントの作成から運用までを支援するスキル群になっています。

ランタイムのアプリは、ふつうの Python の Functions プロジェクトに"エージェント用のファイル"を足した形です。

![Serverless Agent Runtime のプロジェクト構成](/images/poc-azure-functions-skills/runtime-project-anatomy.png)

- **必須**：`function_app.py`（エントリポイント）／`*.agent.md`（エージェント定義）／`host.json`（Functions ホスト構成）／`requirements.txt`（ランタイム＋依存）
- **任意・条件付き**：`agents.config.yaml`（アプリ全体の既定値＝モデルやタイムアウト等）／`mcp.json`（MCP・コネクタ定義）／`tools/`（カスタム Python ツール）／`skills/`（再利用する `SKILL.md`）／`infra/`（azd などの IaC）

#### 動作のレイヤー

ざっくり、こんな層で動きます。

![Serverless Agent Runtime のレイヤー構成](/images/poc-azure-functions-skills/runtime-layers.png)

1. **イベント／トリガー**：HTTP・タイマー・キュー・Blob・Event Grid・Service Bus・コネクタなど、Functions の豊富なトリガーからエージェントを起動できます。
2. **ランタイム**：`.agent.md` などを読み取り、トリガー登録とエージェントの構築をします。
3. **エージェント実行**：Microsoft Agent Framework が、**指示（`.agent.md`）**と**モデル（Azure OpenAI / Foundry）**でエージェントを動かします。
4. **ツール／機能**：リモート MCP・コネクタ・スキル・サンドボックス実行・カスタム Python ツールを、必要に応じて呼びます。
5. **サーバーレス基盤**：Flex Consumption（従量課金）の上で、マネージド ID・Application Insights・VNet 統合・セッション履歴（Blob）・0→N スケールが標準で付いてきます。

---

## セットアップ！

`@azure/functions-skills` の導入には2系統あります。

- `install` … プラグイン登録＋ワークスペース活性化ファイルを一括で置く。具体的には `.github/copilot-instructions.md`（ルーティング）/ `.github/agents/functions-copilot.agent.md` / `.github/copilot/settings.json` / `.vscode/mcp.json`（Azure MCP）/ `.github/hooks/welcome-setup.json`。
- `plugin install` … プラグインの登録だけ。

今回は plugin だけ・ユーザースコープで入れます。

```powershell
npx @azure/functions-skills plugin install --agent ghcp --scope user --no-workspace
```

`copilot` を起動して `/plugin list` に出れば OK。

```text
● Installed Plugins:

    • microsoft-365-agents-toolkit@work-iq v1.1.1
    • workiq@copilot-plugins v1.0.0
    • azure-functions-skills@azure-functions-skills v0.0.4-preview
    • azure@azure-skills v1.1.65
```

---

## Azure Functions Skills を使って開発しよう🚀

では早速使っていきましょー

### 1. 前提を確認する（`azure-functions-setup`）

```text
> Azure Functions 開発の前提（Azure CLI / Core Tools / 言語ランタイム）が揃っているか確認して。
```

依頼の内容に合うスキル `azure-functions-setup` が `description` を手がかりに呼ばれて、足りないものを見つけて導入まで案内してくれます。

スキルがロードされると、Azure CLI、Azure Developer CLI、Azure Functions Core Tools、Python あたりの前提がそろっているかチェックが走ります。
![前提ツール（Azure CLI / azd / Core Tools / Python）の確認結果](/images/poc-azure-functions-skills/2026-06-04-10-51-50.png)

わたしの場合は、一部ツールのバージョンが古いと指摘されましたね。
![一部ツールのバージョンが古いと指摘された様子](/images/poc-azure-functions-skills/2026-06-04-10-57-46.png)

### 2. 設計を相談して、作ってもらう（`azure-functions-agents`）

まずはプランモードで、Azure Functions の上で動くエージェントを作る計画を立ててもらいましょう。
どういうエージェントを作りたいかは、事前に hosted-agent-design.md で設計してあるので、そのファイルを渡して設計してもらいます。

```text
@docs/hosted-agent-design.md の設計思想に従って、顧客プロフィール更新イベント（Event Grid）で起動し、
保有車履歴と家族構成からおすすめ車種を複数提案する Azure Functions のエージェントをPython で作って。
提案はカタログ照会ツールで裏取りして、通知はせず最終応答で返すだけにして。
```
![設計ファイルを渡してプランモードで依頼した様子](/images/poc-azure-functions-skills/2026-06-04-11-53-39.png)

azure-functions-skills をロードして、その中の references を読みながら、Azure Functions でどう実装するのがいいかを考えてくれます。

![references を読みながら実装方針を検討している様子](/images/poc-azure-functions-skills/2026-06-04-11-56-15.png)

スキルは `azure-functions-agents` をロードしたうえで、タスクに必要な参照ファイルだけを読みます。今回読むのは次のあたりです。

- `agent-files.md`（`.agent.md` の書式）
- `triggers.md`（`event_grid_trigger` のスキーマ）
- `tools-and-skills.md`（カスタムツール・スキル）
- `project-files.md`（必要ファイル）

さらに付属の quickstart サンプルも確認します。巨大な知識ベースを抱えつつ、読むのは今回必要な分だけ、というわけですね。
ここが Skill のいいところだと思います。


---
こんな計画が出てきました。
中身を確認して、必要なら修正、問題なければ承認しましょう～。
あとは Autopilot におまかせします。
![生成された実装計画](/images/poc-azure-functions-skills/2026-06-04-12-05-15.png)

#### できあがった子の概要

何ができたかというと、

![車種提案エージェントの構成（生成物）](/images/poc-azure-functions-skills/agent-components.png)

ツールが参照するカタログと顧客プロフィールは、検証なのでリポジトリの中に置いたスタブ JSON です（`data/catalog.json`・`data/profiles.json`）。

`.agent.md` のフロントマターはこんな感じです（ランタイム設定を YAML、振る舞いを markdown で書きます）。

```markdown
---
name: Vehicle Recommendation
description: プロフィール更新イベントで起動し、カタログに接地した車種を提案する。
trigger:
  type: event_grid_trigger
model: $FOUNDRY_MODEL
---
get_profile で顧客情報を取得し、vehicle-matching の指針に従い、
必ず lookup_catalog で裏取りして、おすすめを最終応答で返す。
```

ここで効いてくるのが「プロンプトじゃなくてツールで接地する」という考え方です。存在しない車種や価格を勝手に作らないよう、必ずカタログ照会ツールの結果に基づかせます。ここが AI エージェントの品質の肝です。あとで出てくる `doctor` ともきれいに噛み合ってきます。

:::message
バックグラウンド（イベント駆動）のエージェントには `builtin_endpoints`（チャット UI/API）を付けないのが流儀です。検証は admin エンドポイント＋Application Insights で行います。
:::

とこのブログを書いている間に、実装が終わったようです～
![Autopilot による実装完了の表示](/images/poc-azure-functions-skills/2026-06-04-12-29-44.png)

#### 生成されたもの（実物）

Autopilot が 20 ファイルを生成しました（抜粋）。

```text
.
├─ azure.yaml / .gitignore
├─ infra/
│   ├─ main.bicep            … Foundry + Flex Consumption + RBAC + Monitoring のみ
│   │                          （ACA セッションプール／コネクタは無し）
│   ├─ main.parameters.json
│   └─ app/{api,foundry,rbac}.bicep, abbreviations.json
└─ src/
    ├─ function_app.py        … create_function_app() のみ
    ├─ host.json              … functionTimeout 00:30:00
    ├─ requirements.txt       … azurefunctions-agents-runtime + pydantic
    ├─ agents.config.yaml     … system_tools なし / timeout 1800
    ├─ recommend_vehicle.agent.md   … event_grid_trigger / mcp: false
    ├─ tools/{get_profile,lookup_catalog}.py
    ├─ skills/vehicle-matching/SKILL.md
    └─ data/{catalog,profiles}.json … 13 車種・3 顧客のスタブ
```

event_grid_trigger ／ カタログ接地（`catalog.json`）／ skill 分離 ／ 通知なし ／ セッションプール・コネクタ無し。設計思想どおり、狙ってた構成がそのまま出てきました。

そのまま `func start` でトリガー登録を確認してみます。

```text
Functions:

    recommend_vehicle: eventGridTrigger
```

エラーも出ず、`eventGridTrigger` としてちゃんと登録されました。

### 3. デプロイ前に事故を止める（`azure-functions-doctor`）

`doctor` には入り口が2つあります。

- CLI（`npx @azure/functions-skills doctor`）… 決定論的チェック（Tier 1）＋サプライチェーン検査。`--deep` で LLM 意味解析（Tier 2）も走りますが、このバージョン（0.0.4-preview）には `--deep` がありません。
- Copilot CLI のスキル（`azure-functions-doctor`）… コーディングエージェント自身が意味解析まで行います。CLI の `--deep` が無くても、こちらで深い解析ができます。

まずは CLI の決定論的チェックからいきます。こっちは速いです。

```powershell
npx @azure/functions-skills doctor --dir ./src
```

`host.json` が無い状態だと、何が問題でどう直すかまで出してくれます。

```text
Azure Functions Doctor

Built-in checks:
  ❌ project-exists        host.json is missing
                            Run "func init" or "azure-functions-skills create" to create a project

Summary: 1 problem(s), 0 warning(s), 0 passed
```

Tier 1 は高速チェックとサプライチェーン検査です（固定されていない本番依存、lockfile 欠如、追跡された `.env`、install-script 依存 …）。`--deep`（Tier 2）は、エラーハンドリング漏れ・ブロッキング I/O・秘密情報のハードコードといった意味的な問題を拾います。

#### スキルで意味解析する

Copilot CLI 内で `azure-functions-doctor` を呼ぶと、スキルは Progressive Disclosure で必要なチェックリストだけを読みます。`routing.md` → `ai-semantic-checks.md`／`language-checks.md`（Python）／`supply-chain-checks.md`（requirements.txt あり）／`iac-azure-resource-checks.md`（Bicep あり）、という順番ですね。そのうえでプロジェクトを解析して `doctor-report.json` を出してくれます。

```text
❯ /azure-functions-skills:azure-functions-doctor
```

実行すると、深刻度ごとに整理された解析サマリが出ます（下表）。

いくつか指摘が出てきました。これらも直させましょう！

| 深刻度 | ID | 箇所 | 指摘 |
| --- | --- | --- | --- |
| 🔴 High | SC-005 | `.gitignore` | `local.settings.json` が gitignore されておらず `AccountKey=` を含む。エンドポイントを埋めたら実シークレットを commit しうる |
| 🔴 High | iac-shared-key-access | `infra/main.bicep` | ストレージが managed identity 運用なのに `allowSharedKeyAccess: true`。最小権限のため無効化を |
| 🟡 Med | CQ-007 | `src/tools/get_profile.py` | 顧客が見つからない時に例外でなく `{"error": ...}` を返す → LLM が正常データと誤認してハルシネーションしうる |
| 🟡 Med | CF-local-endpoint-empty | `src/local.settings.json` | `FOUNDRY_PROJECT_ENDPOINT` が空 → ローカル初回実行で失敗 |
| 🟡 Med | SC-008 | `infra/app/api.bicep` | Function App に `minTlsVersion` 未設定（ストレージは TLS 1.2 固定なのに） |
| 🔵 Low | CQ-005 | `recommend_vehicle.agent.md` | Event Grid の at-least-once に対する冪等性ガード無し（今は read-only で無害、書き込みを足すと危険） |
| 🔵 Low | PY-003 | `src/requirements.txt` | `azure-functions` を直接宣言しておらずバージョン固定も無い（推移的依存） |



実際に「直して」と指示すれば、IaC パッチやコード修正として直してくれます（修正後の状態は、次の best-practices で裏取りします）。

#### `--deep`（CLI）のセキュリティモデル

CLI の `--deep` は `--accept-deep-risk` が必須で（エージェントが昇格権限で動くことへの承認）、信頼できる workspace でしか動きません。PR の workspace では実行を拒否します（プロンプトインジェクション対策）。CI で使うなら `push: main`＋GitHub Environment が定石です（後述）。

### 4. 本番に出して大丈夫か（`azure-functions-best-practices`）

```text
> このアプリを本番に出して大丈夫か、Azure Functions のベストプラクティスでレビューして。
```

スキルは `review-checklist.md`／`remediation-patterns.md` を読んで、Azure ベストプラクティス MCP のガイダンスも取りつつ、ソースと IaC を本番レディネスの観点でガッツリ精査してくれます（未デプロイなので、対象はローカルの Bicep・コードです）。

まず嬉しかったのは、前段の `doctor` が挙げた 7 件が、現行ファイルですべて解消済みだったこと（gitignore・`allowSharedKeyAccess`・`get_profile` の `None` 返却・`minTlsVersion`・冪等性注記・azure-functions・エンドポイント設定）。doctor で見つける → 直す → best-practices で裏取り、という流れですね。

そのうえで、より上位の「本番に出してよいか」を判定します。結論は「このままでは不可。Critical 2 件」でした。

![best-practices レビューで Critical 2 件と判定された結果](/images/poc-azure-functions-skills/2026-06-04-19-31-51.png)

| 深刻度 | 問題 | 箇所 | なぜ効く |
| --- | --- | --- | --- |
| 🔴 Critical | スタブデータを本番顧客に返す | `src/data/*.json` | 実顧客 DB・カタログ API へ差し替え必須 |
| 🔴 Critical | Event Grid サブスクリプションが IaC に無い | `infra/main.bicep` | デプロイは成功するのにイベントが届かず、エージェントが一切起動しない |
| 🔴 High | モデル自動アップグレード（`versionUpgradeOption`） | `infra/app/foundry.bicep` | 出力フォーマット・挙動が無通知で変わる → `NoAutoUpgrade` に |
| 🔴 High | `ftpsState` 未設定 | `infra/app/api.bicep` | `Disabled` を明示 |
| 🟡 Med | `maximumInstanceCount: 100` × 30 分 AI | `infra/app/api.bicep` | コスト爆発の恐れ。初期は 5〜10 に |
| 🟡 Med | ログ保持 30 日 / 障害アラート無し / リージョン US 限定 / Preview API | `main.bicep`・`foundry.bicep` | 運用・監視・移植性の穴 |
| 🟢 Low | コールドスタート・不要 CORS・スロット未検討 | infra | PoC では許容、本格運用で対応 |

特にいいなと思ったのが「Event Grid サブスクリプションが IaC に無い」の指摘です。Bicep は通るしデプロイも成功する。なのにイベントが来ないからエージェントが動かない。手で書くと気づきにくい「成功して見えるのに動かない」罠を、本番レディネスの観点が先回りで拾ってくれました。

一方で、lean に削いだ設計はセキュリティ面では合格でした。`allowSharedKeyAccess: false`＋ID ベースストレージ、`httpsOnly`＋`minTlsVersion 1.2`、マネージド ID の最小権限 RBAC、App Insights の AAD 認証、Flex Consumption FC1、agent timeout < host timeout … といったあたりですね。

スキルは優先度ロードマップまで出してくれます。

- 本番前に必須 → データソース差し替え／Event Grid サブスクリプションを IaC へ
- リリース直前 → 自動アップグレード無効化／FTPS 無効／最大インスタンス数
- リリース後 1 sprint → ログ保持・アラート・リージョン拡張

「直して」と言えば、IaC パッチやコード修正として、承認ゲート付きで適用までやってくれます。

### 5. デプロイする（`azure-functions-deploy` → Azure Skills）

```powershell
az login
az account show
```

```text
> このエージェントを Azure にデプロイして。
```

`azure-functions-deploy` は、Azure Skills（`azure-prepare` → `azure-validate` → `azure-deploy`）へ委譲するプロキシ的な役割です（導入済みなのは前掲の `/plugin list` の `azure@azure-skills`）。
`az`/`azd` のログインを確認したうえで、prepare（`azure.yaml`・Bicep などデプロイ準備の整合チェック）→ validate（事前検証）→ deploy の順に進み、azd 環境（`vehicle-agent` / `japaneast`）でプロビジョニングからコードデプロイまで一気通貫で進めてくれます。
Functions 固有の判断は Functions Skills が、汎用の Azure デプロイは Azure Skills が担当する分担ですね！
Skillの使いこなしとして勉強になります。

![prepare → validate → deploy が進行する様子](/images/poc-azure-functions-skills/2026-06-04-22-17-27.png)

作成されたリソース（実測。環境 `vehicle-agent` / `rg-vehicle-agent` / `japaneast`）：

| リソース | 名前 |
| --- | --- |
| Function App（Flex Consumption FC1） | `func-agents-5uq4jqomnf3jk` |
| Storage Account | `st5uq4jqomnf3jk` |
| Microsoft Foundry（`gpt-4.1`） | `cog-5uq4jqomnf3jk` |
| Application Insights / Log Analytics | `appi-…` / `log-…` |
| Event Grid Topic | `evgt-customer-profile-5uq4jqomnf3jk` |
| Event Grid Subscription | `sub-recommend-vehicle` |

デプロイされた関数は `recommend_vehicle`（EventGrid トリガー）、エンドポイントは `https://func-agents-5uq4jqomnf3jk.azurewebsites.net/` です。リソース一覧に ACR はありません。最初に触れたとおり、コンテナを一切作らずソースから上がりました。

:::message
シークレットはチャットに流さないこと。エージェントは managed identity 前提（秘密情報をコードに書かない）で設計します。
:::

:::message alert
ハマりどころ（Event Grid サブスクリプション）。best-practices の指摘（C-2）を受けて、Event Grid トピックは IaC に入れ、サブスクリプションは postdeploy フックで配線する形にしました。ところがそのフックが webhook 検証で 401。Copilot が切り分けたところ、webhook 自体は直接叩けば 200（検証応答 OK）で、真因は `az eventgrid` コマンドが VS Code（Electron）経由で引数破損していたことでした。最終的に `az rest` で Event Grid の REST API を直接叩いてサブスクリプションを作成し、`Succeeded` まで持っていきました。「Bicep は通る・デプロイも成功するのにイベント配線でつまずく」。まさに C-2 の「成功して見える罠」を実地で踏んで、自力で抜けた一幕でした。
:::

### 6. 動いているか・どんな構成か（`azure-functions-health-status` / `azure-functions-inventory`）

```text
> デプロイした Function App の状態と健全性を見て。
```

`azure-functions-health-status` は付属の PowerShell スクリプトで、アプリ状態・Resource Health・プラン状態・Azure Monitor メトリクス・直近の Activity Log を取得します。

![health-status スクリプトによる稼働状態の取得結果](/images/poc-azure-functions-skills/2026-06-04-22-44-05.png)

| 項目 | 結果 |
| --- | --- |
| アプリ状態 / ランタイム | Running（Normal）/ Normal |
| プラン（Flex Consumption FC1） | Ready |
| Resource Health | 取得不可（FC1 は未サポート） |
| メトリクス（24h） | インスタンス avg ~1.05 / CPU max 1% / メモリ ~574MB / 実行 0 |
| トリガー | `recommend_vehicle`（EventGrid, CustomerProfileUpdated）有効 |
| Activity Log | デプロイ操作のみ・エラーなし |

インベントリ（`azure-functions-inventory`）も付属スクリプトで取れます。「この Function App の構成インベントリ（SKU/プラン・ランタイム・設定・関数/トリガー一覧）を出して」と頼むと、構成をギャップなく一覧にしてくれます（実測・抜粋）。

![インベントリ：SKU・プラン情報](/images/poc-azure-functions-skills/2026-06-04-23-13-46.png)

![インベントリ：ランタイム・アプリ設定](/images/poc-azure-functions-skills/2026-06-04-23-14-01.png)

![インベントリ：関数・トリガー一覧](/images/poc-azure-functions-skills/2026-06-04-23-14-21.png)

### 7. 動作検証する

イベント駆動エージェントなので、
1. Event Grid トピックに実イベントを発行
2. サブスクリプション経由で `recommend_vehicle` が起動
3. 結果は Application Insights／セッション履歴に出る

という流れで確認します。

```powershell
# トピックの endpoint と key（az eventgrid は VS Code 経由で引数破損しがちなので az resource/az rest で）
$sub = az account show --query id -o tsv
$base = "/subscriptions/$sub/resourceGroups/rg-vehicle-agent/providers/Microsoft.EventGrid/topics/evgt-customer-profile-5uq4jqomnf3jk"
$endpoint = az resource show --ids $base --query properties.endpoint -o tsv
$key = az rest --method post --uri "https://management.azure.com$base/listKeys?api-version=2022-06-15" --query key1 -o tsv

# CustomerProfileUpdated を発行（customer_id は profiles.json の実在 ID）
$body = '[{"id":"t1","eventType":"CustomerProfileUpdated","subject":"customers/C003","eventTime":"2026-06-05T00:00:00Z","dataVersion":"1.0","data":{"customer_id":"C003"}}]'
Invoke-RestMethod -Method Post -Uri $endpoint -Headers @{ "aeg-sas-key" = $key } -ContentType "application/json" -Body $body
```

`200`（空ボディ）で受理されます。1〜3分後、`AppRequests` に `recommend_vehicle` が `Success`（所要 ≈15 秒）で現れました。

```text
Executing 'Functions.recommend_vehicle' (Reason='EventGrid trigger fired ...')
DefaultAzureCredential acquired a token from ManagedIdentityCredential   ← 秘密ゼロ（MI）
Function name: get_profile        （ツール：プロフィール取得）
Function name: load_skill         （vehicle-matching を“実行時”にロード）
Function name: lookup_catalog     （ツール：カタログ照会＝接地）
Executed 'Functions.recommend_vehicle' (Succeeded, Duration≈15s)
```

確認ポイントは、 `load_skill` が「実行時のツール呼び出し」として出ているところですね。
順序も `get_profile`（家族構成）→ `vehicle-matching`（指針）→ `lookup_catalog`（カタログ照会）と、設計したフローでちゃんと動いてます。

最終応答はこんな感じです（C003 ＝大人2＋子3＋祖父母同乗で 7 人必要。最終応答は、ランタイムが実行ごとに `AzureWebJobsStorage` の Blob へ自動記録するセッション jsonl から取得しました）。

```json
{
  "customer_id": "C003",
  "customer_name": "佐藤 次郎",
  "recommendations": [
    { "model_name": "シエンタ",   "seats": 7, "monthly_price_jpy": 38000,
      "reason": "7人乗り・3列シートでご家族全員と祖父母も一緒に乗れるサイズ。スライドドアで乗降も安心。" },
    { "model_name": "ヴォクシー", "seats": 7, "monthly_price_jpy": 52000,
      "reason": "7名で快適に使えるミニバン。多人数の通勤・お出かけに。" },
    { "model_name": "アルファード", "seats": 7, "monthly_price_jpy": 98000,
      "reason": "ゆとりある室内空間。3列プレミアムシートや安全装備も充実し、長距離移動にも安心。" }
  ]
}
```

3車種とも、価格はすべて `catalog.json` 由来でハルシネーションはありません。しかも家族構成に紐づいて 7 人乗りミニバンにちゃんと絞り込まれています。`get_profile`→`vehicle-matching`→`lookup_catalog` の効果が一目で分かりますね。

### 8. つまずいたら（`azure-functions-diagnostics`）

デプロイ失敗・トリガー不発・例外などが出たら、

```text
> recommend_vehicle が想定どおり動かない。原因を診断して。
```

`azure-functions-diagnostics` が、deployment/runtime/trigger/binding/language worker/telemetry のログ解析と是正案を返してくれます。
嬉しいことですが、今回は失敗が無かったので出番なしでした！！

### 9. 気づきを次に活かす（`azure-functions-feedback`）

`azure-functions-feedback` が、セッションで見つけたこと（誤り・分かりにくさ・preview の差分）をプレビュー付きで Issue/PR の下書きにしてくれます（投稿は任意）。
preview のうちに足りないところを還元できる、気の利いた導線ですね！開発にフィードバックする心理的？ハードルが下がります！

これも、開発者として普段からリポジトリに用意しておきたいなと思ったスキルでした。

---

## おわりに

Azure Functions Skills を使って、Azure 上で動く AI エージェントを作ってみました。エージェントの設計からコード生成、デプロイ前のチェック、ベストプラクティスレビュー、デプロイ、動作確認まで、一通りの流れを体験できましたね。

今回は検証なのでスタブデータでしたが、実際に運用するなら、データソースの差し替えや、`doctor --deep` を組み込んだ CI 連携あたりが次のステップになりそうです。

今後はサービスごとに、こういったコーディングエージェントのためのスキルセットがどんどん充実していくと思います。

---

## 参考リンク

- Azure Functions Skills（GitHub）: https://github.com/Azure/azure-functions-skills
- Azure Functions Skills 公開アナウンス（Azure updates / Build 2026）: https://azure.microsoft.com/en-us/updates?id=562482
- サーバーレスエージェントランタイム（概念）: https://learn.microsoft.com/azure/azure-functions/functions-serverless-agents-runtime
- 同 quickstart（azd でデプロイ）: https://learn.microsoft.com/azure/azure-functions/scenario-serverless-agents-runtime
- Foundry の Hosted Agents（別物・コンテナ型／ソース直デプロイ preview）: https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents
- Azure MCP × GitHub Copilot CLI: https://learn.microsoft.com/azure/developer/azure-mcp-server/how-to/github-copilot-cli
- Azure Skills（委譲先）: https://github.com/microsoft/azure-skills
- Microsoft Build 2026（公式）: https://news.microsoft.com/build-2026/
