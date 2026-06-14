# OneManCompany を Azure Microsoft Foundry の gpt-5.4-nano で動かす — 実行記録ログ

> このファイルは Zenn 記事化のための「実行記録(生ログ)」です。体裁は後で整えます。
> 作業日: 2026-06-05 / 環境: Windows 11, PowerShell

## ゴール

OSS の [OneManCompany](https://github.com/1mancompany/OneManCompany)(AI 社員が自律的に働く「会社の OS」)を、
デフォルトの OpenRouter ではなく **Azure Microsoft Foundry にデプロイした gpt-5.4-nano** で動かす。

---

## 1. 事前調査:OneManCompany の LLM 接続アーキテクチャ

### わかったこと

- OneManCompany は Python (FastAPI + LangChain/LangGraph) + フロントエンドの構成。`npx @1mancompany/onemancompany` または `bash start.sh` で起動。
- LLM プロバイダ設定は `src/onemancompany/core/config.py` の `PROVIDER_REGISTRY` に集約されている。
- 実際の LLM クライアント生成は `src/onemancompany/agents/base.py` の `make_llm()`。
  - OpenAI 互換プロバイダ → `langchain_openai.ChatOpenAI(model, api_key, base_url, ...)` を生成。
  - Anthropic → `ChatAnthropic`。
- 設定の優先順位:従業員ごとの `profile.yaml`(`api_provider` / `llm_model` / `api_key`)→ 会社デフォルト(`.onemancompany/.env` の `Settings`)。

### キーになる「custom」プロバイダ

`PROVIDER_REGISTRY` には `custom` プロバイダがあり、以下で**任意の OpenAI 互換エンドポイント**を指定できる:

| .env キー | 役割 |
| --- | --- |
| `DEFAULT_API_PROVIDER=custom` | プロバイダを custom に |
| `DEFAULT_API_BASE_URL=...` | 任意のエンドポイント URL |
| `CUSTOM_API_KEY=...` | API キー |
| `CUSTOM_CHAT_CLASS=openai` | API 形式(openai / anthropic) |
| `DEFAULT_LLM_MODEL=...` | モデル名(Azure ではデプロイ名) |

`make_llm()` の該当ロジック(抜粋):

```python
if api_provider == "custom" or (settings.default_api_base_url and api_provider == settings.default_api_provider):
    base_url = settings.default_api_base_url
...
return ChatOpenAI(model=model, api_key=effective_key, base_url=base_url, ...)
```

→ `ChatOpenAI` は内部で OpenAI Python SDK を使い、認証は `Authorization: Bearer <key>` ヘッダ。

> 補足:README の TODO には「More LLM provider options (Ollama local, Azure OpenAI, AWS Bedrock, etc.)」とあり、
> Azure OpenAI の**ネイティブ対応は未実装**。今回は `custom` プロバイダ経由で実現する方針。

---

## 2. Azure Foundry 側の接続仕様(Microsoft Learn で確認)

Azure OpenAI in Microsoft Foundry には **v1 API**(OpenAI 互換)がある:

- エンドポイント: `https://<resource>.openai.azure.com/openai/v1/`
  - `https://<resource>.services.ai.azure.com/openai/v1/` も可
- **API キー認証が標準の `OpenAI()` クライアントでそのまま動く**(= `Authorization: Bearer` ヘッダで API キーを送る形を受け付ける)
- `api-version` クエリは v1 GA では**不要**
- chat completions 構文に対応(OpenAI モデルだけでなく DeepSeek/Grok 等も)

```python
# Microsoft Learn のサンプル(API Key 認証)
from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url="https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/",
)
```

### 結論(設計判断)

`langchain_openai.ChatOpenAI` は OpenAI SDK と同じ Bearer 認証なので、
**OneManCompany 側はコード変更不要**。`.onemancompany/.env` を以下に設定すれば動くはず:

```env
DEFAULT_API_PROVIDER=custom
DEFAULT_API_BASE_URL=https://<resource>.openai.azure.com/openai/v1/
CUSTOM_API_KEY=<Azure Foundry の API キー>
CUSTOM_CHAT_CLASS=openai
DEFAULT_LLM_MODEL=<gpt-5.4-nano のデプロイ名>
```

> Azure では `model` パラメータに**デプロイ名**を渡す点に注意(モデル名そのものではない)。

---

## 3. Azure 環境の確認(これから)

- サブスクリプション(`az account` / MCP `subscription_list` で確認済み):
  - `shirokuma`(既定): `f80766c9-6be7-43f9-8369-d492efceff1e`
  - `Visual Studio Enterprise サブスクリプション`: `3a9c7a75-8f41-4adf-9969-2965d655bc36`
### 既存の Cognitive Services / Foundry リソース(shirokuma サブスク)

`az cognitiveservices account list` の結果:

| 名前 | kind | リージョン | RG |
| --- | --- | --- | --- |
| ai-poc-eastus2-resource | AIServices | eastus2 | rg-ai-poc-eastus2 |
| ai-agent-udemy-learn-01-resource | AIServices | eastus2 | rg-ai-agent-udemy-learn-01 |
| dma-foundry-poc-cpi4bxdl | AIServices | eastus2 | rg-durable-manage-poc |
| shirono-qa-prod-openai-3h4vj5av3j2ea | OpenAI | japaneast | rg-shirono-qa-prod |
| cog-5uq4jqomnf3jk | AIServices | japaneast | rg-vehicle-agent |
| (Speech / FormRecognizer は対象外) | | | |

### 既存デプロイ

`ai-poc-eastus2-resource` が最も充実(GPT-5 ファミリーあり):
`gpt-5`, `gpt-5-mini`, `gpt-5-chat`, `gpt-5.1`, `gpt-5.2`, `gpt-4.1`, `gpt-4o`, `gpt-image-*`, `sora-2`, embeddings など。

→ **しかし `gpt-5.4-nano` はどのアカウントにも未デプロイ**。

### モデルカタログ確認:gpt-5.4-nano は実在する

`az cognitiveservices account list-models`(ai-poc-eastus2-resource / eastus2)で
`gpt-5.4-nano`(**version 2026-03-17, format OpenAI**)がカタログに存在しデプロイ可能と確認。
同ファミリーで `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-pro`, さらに `gpt-5.5` も利用可能。

### 方針

`gpt-5.4-nano` を `ai-poc-eastus2-resource`(eastus2)に新規デプロイ →
エンドポイント `https://ai-poc-eastus2-resource.cognitiveservices.azure.com/openai/v1/` + API キーで
OneManCompany の `custom` プロバイダに接続する。

> 注:Foundry(AIServices kind)のエンドポイントは `*.cognitiveservices.azure.com`。
> v1 OpenAI 互換パスは `<endpoint>/openai/v1/`。

### 既存デプロイを利用(ユーザー回答)

CEO(ユーザー)に確認したところ、**既に別サブスクにデプロイ済み**だった:

- サブスクリプション: `genai`(`605923aa-f343-4a7d-b44f-c4599c81e059`)
- リソース: `dev-genai-swedencentral-resource`(AIServices, **swedencentral**, RG: `dev-swedencentral`)
- デプロイ名: **`gpt-5.4-nano-nomura`**(model: gpt-5.4-nano / version 2026-03-17 / GlobalStandard / capacity **26259** ≒ 26M TPM)

`az cognitiveservices account list` を default サブスクだけ見ていたため最初は見つからず。
`az account list --all` で全テナント/サブスクを洗い出し → `genai` サブスクで発見した。

リソースのエンドポイント(抜粋):

- AI Foundry / Model Inference API: `https://dev-genai-swedencentral-resource.services.ai.azure.com/`
- Azure OpenAI Legacy: `https://dev-genai-swedencentral-resource.openai.azure.com/`

→ OpenAI 互換 v1 で使うのは **`https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/`**。

---

## 4. 疎通テスト(コード変更前の事前検証)

OneManCompany を触る前に、`ChatOpenAI` と同じ **Bearer 認証**で v1 chat/completions が通るかを単体検証:

```powershell
$key1 = (az cognitiveservices account keys list --name dev-genai-swedencentral-resource `
  --resource-group dev-swedencentral --subscription 605923aa-... -o json | ConvertFrom-Json).key1
$base = "https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1"
$body = @{ model = "gpt-5.4-nano-nomura"; messages = @(@{ role="user"; content="Reply with exactly: OMC-OK" }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri "$base/chat/completions" `
  -Headers @{ "Authorization" = "Bearer $key1"; "Content-Type" = "application/json" } -Body $body
```

結果(成功):

```
model:   gpt-5.4-nano-2026-03-17
content: OMC-OK
usage:   prompt=14 completion=8
```

> ✅ **重要**:Azure Foundry の v1 エンドポイントは API キーを `Authorization: Bearer` で受け付ける。
> `api-key` ヘッダも `api-version` クエリも不要。
> これで `langchain_openai.ChatOpenAI`(OpenAI SDK = Bearer 認証)がそのまま使えると確定。
> → OneManCompany 側は **コード変更ゼロ**で `custom` プロバイダ設定だけで接続できる。
>
> (APIキーは本ログでは秘匿。`az ... keys list` で取得した key1 を使用。)

## 5. OneManCompany のセットアップ(Windows / dev モード)

`start.sh` は bash + POSIX venv 前提なので、Windows では uv を直接使う。

```powershell
cd C:\Users\HirokiNomura\workspaces\PoC\OneManCompany
uv venv --python 3.12
uv pip install -e .
```

(uv 0.9.8 / Python 3.12.9 / Node 24。コンソールスクリプトは `onemancompany`=サーバ、`onemancompany-init`=ウィザード)

### オンボーディングの肝

`onemancompany-init` のウィザード(`onboard.py`)は対話式だが、`--auto -y` で非対話実行できる。
`run_auto()` は **プロジェクトルートの `./.env`** を読み、最終的に `.onemancompany/.env` を生成する。

ただし `run_auto()` は `_step_execute()` に `base_url` / `custom_chat_class` を**渡さない**実装になっており、
生成される `.onemancompany/.env` から `DEFAULT_API_BASE_URL` と `CUSTOM_CHAT_CLASS` が**抜け落ちる**。
→ auto-init 後に手動で追記する必要がある(ここがハマりどころ)。

### 手順

1. ルート `./.env` を作成(custom プロバイダ検出用):

   ```env
   DEFAULT_API_PROVIDER=custom
   CUSTOM_API_KEY=<key>
   DEFAULT_API_BASE_URL=https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/
   CUSTOM_CHAT_CLASS=openai
   DEFAULT_LLM_MODEL=gpt-5.4-nano-nomura
   HOST=0.0.0.0
   PORT=8000
   ```

2. 非対話 init:

   ```powershell
   .\.venv\Scripts\onemancompany-init.exe --auto -y
   ```

   出力(抜粋):

   ```
   Provider: custom / Model: gpt-5.4-nano-nomura
   ✔ Company template copied
   ✔ .env written
   sync_founding_defaults: updated 00001..00005 → provider=custom, model=gpt-5.4-nano-nomura
   ✔ Founding employees set to custom/gpt-5.4-nano-nomura
   G E N E S I S   C O M P L E T E
   ```

3. 生成された `.onemancompany/.env` に欠落2キーを追記:

   ```
   DEFAULT_API_BASE_URL=https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/
   CUSTOM_CHAT_CLASS=openai
   ```

4. 創業メンバーのプロフィール確認(例: EA `00004/profile.yaml`):

   ```yaml
   api_provider: custom
   hosting: company
   llm_model: gpt-5.4-nano-nomura
   ```

---

## 6. エンドツーエンド検証(OMC のコードパス経由)

サーバ起動前に、OMC が実際にエージェント生成で使う `make_llm()` を直接叩いて検証した。

```python
from onemancompany.core.config import settings
from onemancompany.agents.base import make_llm
llm = make_llm("00004")   # EA founding agent
resp = await llm.ainvoke("Reply with exactly: OMC-AZURE-OK")
```

結果:

```
=== make_llm('00004') ===
class   : ChatOpenAI
model   : gpt-5.4-nano-nomura
base_url: https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/

=== live ainvoke ===
content   : OMC-AZURE-OK
resp model: gpt-5.4-nano-2026-03-17
usage     : input=17 output=11 total=28
```

> ✅ OMC の従業員ランタイムが **Azure Foundry の gpt-5.4-nano** を使うことを、
> 実際のコードパス(`make_llm` → `ChatOpenAI` → ライブ呼び出し)で確認。
> `usage_metadata` も取れているのでコスト集計も機能する。

## 7. サーバ起動

`start.sh` を使わず uv 経由で直接起動(Windows):

```powershell
.\.venv\Scripts\onemancompany.exe   # uvicorn 0.0.0.0:8000 をフォアグラウンド起動
```

起動ログ(抜粋):

```
[startup] Registered Pat EA / Sam HR / Alex COO / Morgan CSO / CEO (00001..00005) — LangChainExecutor
System crons started: ['heartbeat','review_reminder','config_reload',...]
Application startup complete.
🏢 One Man Company HQ v0.7.85 is running!  Frontend: http://localhost:8000
```

- `GET /` → HTTP 200(ピクセルアートのオフィス UI が表示)
- ERROR / 401 / 403 / missing-api-key は無し
- 注:`self-improving-agent` スキルの hook スクリプト未配置の WARNING は出るが無害

ブラウザで `http://localhost:8000` を開くと、AI 社員(EA/HR/COO/CSO)が着席したオフィスが表示される。

## 8. 実タスク投入(会社を gpt-5.4-nano で動かす)

CEO 指示を `POST /api/ceo/task`(multipart form)に投入:

```powershell
$task = "会社の最初のブログ記事のドラフトを作ってください。テーマは『AI社員だけで運営する一人会社（OneManCompany）とは何か』。日本語で600〜800字、見出し付き。完成したらプロジェクトのworkspaceにmarkdownで保存してください。"
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/ceo/task" -Form @{ task=$task; mode="simple" }
```

レスポンス:

```json
{ "routed_to": "EA", "status": "processing",
  "project_id": "e9ef65fcb226", "iteration_id": "iter_001" }
```

### 自律実行の流れ(サーバログ)

```
POST /api/ceo/task 200 OK
Project e9ef65fcb226 renamed: '会社の最初のブログ記事…' → 'AI社員だけのOneManCompanyとは'   ← LLMが命名
[PROJECT COMPLETE] EA node a2bee8e21d6d done + all subtrees resolved — scheduling CEO confirmation
[CeoExecutor] Enqueued request for project=e9ef65fcb226/iter_001 …
```

EA エージェントが使ったツール(`verification.json` より):
`set_project_name → write → read → glob_files → report_to_ceo`
(= プロジェクト命名 → 記事執筆 → 保存 → 内容確認 → CEO報告 を自律実行)

### 成果物:`company/first_blog_draft.md`(1709 bytes)

```markdown
# AI社員だけで運営する一人会社（OneManCompany）とは何か

## はじめに
OneManCompanyは、「人を増やす」ことで成長するのではなく、AIを“社員”として迎え入れ、
運営の仕組みごと外部化する一人会社です。…

## AI社員とは何をするのか
…（企画、要件整理、文章作成、レビュー観点の提示、タスク分解、進捗記録 …）

## なぜ一人会社なのか / 下流まで考える運営 / これからの姿
…完了条件は「次へ手渡せた状態」…
```

見出し付き・約700字の日本語ドラフトが自動生成された(製品レベルの出力)。

### 使用モデルの確定的な証拠

`iterations/iter_001/debug_trace.jsonl` を集計:

```
model = gpt-5.4-nano-2026-03-17   in=152918  out=925
```

> ✅ **会社の実フロー(CEO指示 → EAが自律実行 → 成果物 → CEO報告)が、
> 丸ごと Azure Microsoft Foundry の gpt-5.4-nano 上で動いた**ことを確認。
> (入力トークンが大きいのは、ReAct の各ステップでシステムプロンプト+ツールスキーマを毎回送るため。nano なので低コスト)

---

## 9. まとめ / ハマりどころ / 再現手順

### 結論

OneManCompany は **Azure Microsoft Foundry の v1(OpenAI互換)エンドポイント**に、
**コード変更ゼロ**・`custom` プロバイダ設定だけで接続できる。
鍵は「Azure v1 は API キーを `Authorization: Bearer` で受け付ける」ため、
`langchain_openai.ChatOpenAI` がそのまま使えること。

### ハマりどころ

1. **エンドポイントの形**:`/api/projects/...`(プロジェクトエンドポイント)ではなく、
   リソースレベルの `https://<resource>.services.ai.azure.com/openai/v1/` を使う。
   `*.openai.azure.com/openai/v1/` でも可。
2. **`model` にはデプロイ名**を渡す(モデル名ではない)。今回は `gpt-5.4-nano-nomura`。
3. **auto-init が base_url/chat_class を落とす**:`onemancompany-init --auto` は
   `DEFAULT_API_BASE_URL` と `CUSTOM_CHAT_CLASS` を生成 `.env` に書かない。**後追記**が必須。
4. **リソース探索**:`az cognitiveservices account list` は既定サブスクのみ。
   `az account list --all` で全テナント/サブスクを洗い出すこと。
5. **Windows**:`start.sh`(bash前提)ではなく uv 直叩きで venv 作成・起動。

### 再現手順(最小)

```powershell
# 0) 前提: uv, Python 3.12, az CLI(ログイン済み)
cd OneManCompany
uv venv --python 3.12
uv pip install -e .

# 1) Azure 側のキー取得(デプロイは作成済みとして)
$key = (az cognitiveservices account keys list `
  --name dev-genai-swedencentral-resource --resource-group dev-swedencentral `
  --subscription <genai-sub-id> -o json | ConvertFrom-Json).key1

# 2) ルート .env(custom プロバイダ検出用)
@"
DEFAULT_API_PROVIDER=custom
CUSTOM_API_KEY=$key
DEFAULT_API_BASE_URL=https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/
CUSTOM_CHAT_CLASS=openai
DEFAULT_LLM_MODEL=gpt-5.4-nano-nomura
HOST=0.0.0.0
PORT=8000
"@ | Set-Content .\.env -Encoding utf8

# 3) 非対話 init → 生成 .env に2キー追記
.\.venv\Scripts\onemancompany-init.exe --auto -y
Add-Content .\.onemancompany\.env "DEFAULT_API_BASE_URL=https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/"
Add-Content .\.onemancompany\.env "CUSTOM_CHAT_CLASS=openai"

# 4) 起動
.\.venv\Scripts\onemancompany.exe   # → http://localhost:8000
```

### 最終 `.onemancompany/.env`(キーは秘匿)

```env
DEFAULT_API_PROVIDER=custom
CUSTOM_API_KEY=***
DEFAULT_LLM_MODEL=gpt-5.4-nano-nomura
HOST=0.0.0.0
PORT=8000
DEFAULT_API_BASE_URL=https://dev-genai-swedencentral-resource.services.ai.azure.com/openai/v1/
CUSTOM_CHAT_CLASS=openai
```

### 後片付け（必要なら）

```powershell
.\.venv\Scripts\onemancompany.exe stop   # or サーバプロセスを終了
# Azure デプロイは課金(従量)。不要なら:
# az cognitiveservices account deployment delete --name dev-genai-swedencentral-resource `
#   --resource-group dev-swedencentral --deployment-name gpt-5.4-nano-nomura --subscription <genai-sub-id>
```

(Azure接続編 完)

---

# 続編:NORR株式会社の AI組織構築 & 日本語化(実行記録 / 2026-06-06)

> 上の Azure 接続環境をベースに、OMC を NORR株式会社の AI組織として運用。さらに中国語混じり出力の解消(日本語化)とフォーク運用までを記録。

## 10. 方針(NORR を OMC 上に立ち上げる)

NORR株式会社(「あらゆる業界・業種に、IT と AI を。」AI/ITコンサル&開発)を OMC の AI組織として実体化。
- 範囲:稼働中 OMC を NORR化(方向性/文化/組織/採用/SOP/初回PJ)
- 事業4ライン:コンサル(研修/コーチング/伴走/QA)・Web制作・自社プロダクト・マーケ
- 拡張経営層:CTO / CFO・管理 / PdM(OMCに標準C-suiteは EA/HR/COO/CSO のみ。追加分はレベル≤3のシニア社員=役割ラベルで委任ツリー統括)
- 調達:ハイブリッド(既定ローカル、必要時のみ Talent Market remote)
- LLM:役割でティアリング(nano / mini / gpt-5.5)

## 11. 会社の方向性・文化・SOP(API設定)

```text
PUT  /api/company/direction  { "direction": "<NORRミッション…>" }   # 全社員のsystem promptにpriority40で注入
POST /api/company-culture     { "content": "<各価値観>" } ×5
PUT  /api/workflows/{name}     { "content": "<workflow markdown>" }  # SOP 8本
```

SOP 8本:`ai_training_design` / `companion_4steps` / `coaching_3phases` / `web_build` / `online_qa` / `product_dev` / `content_marketing` / `finance_ops`

ハマり:`PUT /api/workflows` は `save_workflow` がスキーマ検証する。**H1 + `**Flow ID**`/`**Owner**` 必須**、各 `## Phase N:` に **`**Goal**`/`**Responsible**` 必須**。準拠すれば保存OK。

## 12. AI社員の採用(ローカル / hire-from-cv)

- `POST /api/candidates/hire-from-cv` で `general-assistant` ベースをカスタム採用。`cv` に name/role/skills/llm_model/hosting を指定。
- **`llm_model` を指定するとティアリングが効く**(検証:CTO採用→profile.yaml に `gpt-5.5-nomura` が保持される)。`api_provider` は会社デフォルト(custom)継承(`use_talent_llm_config=false`)。
- 採用後、COO が自動で department 配属。
- **ハマり**:採用ごとに `employees/{id}/run.py` が生成され、code-watcher(`main.py`)が .py 変更を検知して **graceful restart** を誘発。一括採用直後は再起動が連発するので、**逐次採用+接続リトライ**で対処。

モデルティア:
- nano(`gpt-5.4-nano-nomura`):EA / 下書き・QAトリアージ
- mini(`gpt-5.4-mini-nomura`):HR / CSO / CFO / Webエンジニア / プロダクトエンジニア / マーケター
- top(`gpt-5.5-nomura`):COO / CTO / PdM / AIコンサル
(各 `employees/{id}/profile.yaml` の `llm_model` で設定。`prompts/role.md` で NORR役割特化)

## 13. 初回PJで E2E検証(マルチエージェント+ティアリング)

`POST /api/ceo/task`(standard)に「建設業80名向けAI研修カリキュラム(3軸)+3ヶ月コーチング案」を投入 →
- EA→COO が11ノードに分解、AIコンサル/PdM/CSO が分担して成果物生成。
- `debug_trace.jsonl` 集計:`gpt-5.5`×4 / `gpt-5.4-mini`×4 / `gpt-5.4-nano`×1 → **役割別ティアリングが実機で稼働**。
- 成果物は NORR 方針(3軸=レベル×ドメイン×ツール / 理論20%実践80% / 顧客の自立)準拠。

## 14. 中国語出力の原因特定と日本語化

症状:時々 AI社員の出力が中国語(例:EAサマリ「已完成对CEO指派任务…」)。

原因(複合):
1. **中国語の花名(ニックネーム)がプロンプトに注入** … 各自の自己紹介(`agents/common_tools.py:572`)とチーム名簿(`agents/base.py:1017`)。OMCは設計上、武侠風の中国語花名を生成(`agents/onboarding.py`)。
2. **出力言語を固定する指示が無い**(コードに言語ロック無し)。
3. **会話履歴の中国語残渣**で固定化。
4. **ハードコードの中国語文字列**(`api/routes.py:7452` プロダクト企画キックオフ、`core/product.py` レビューラベル、`core/routine.py` 振り返り表記)。

対策:
- 全社員を**日本語名**(漢字フルネーム+漢字ニックネーム)にリネーム。
- `PUT /api/company/direction` に **「言語ルール(最優先)=必ず日本語で回答」** を追記。
- ハードコード中国語を日本語化(routes/product/routine)。→ .py 変更につき**要サーバ再起動**。
- 花名プール `company/human_resource/nicknames.txt` を**日本語名60件**へ+`onboarding.py` 枯渇時フォールバックも日本語漢字に。
- dev プレビュー(`frontend/floor-picker.html` / `office-preview.html`)も日本語化(ラベル依存のJSロジック `includes('行政')→'役員'` も整合)。

## 15. フォーク運用(日本語版の管理)

直接cloneだと push 不可+CLI の "refresh source by default"(commit 8f880c0)で**ローカル編集が上書きされる恐れ**。→ 公開フォークへ。

```powershell
gh repo fork 1mancompany/OneManCompany --clone=false --remote=false   # → nomhiro/OneManCompany
git remote rename origin upstream
git remote add origin https://github.com/nomhiro/OneManCompany.git
git checkout -b ja        # 日本語化を ja ブランチにコミット&push(ff5438e / 20a8686 / 3417595)
```
- `origin`=フォーク, `upstream`=本家。upstream追従は `git fetch upstream && git merge upstream/main`。
- `.env`(Azureキー)・`.onemancompany/`(組織データ)は **gitignore 済みでコミットされない**。作業ディレクトリ・組織データは維持(再clone不要)。

## 16. 日本語化の動作確認

- 新規採用 `00014` のニックネーム=**「七海」(日本語プール由来)** → 花名修正OK。
- `POST /api/ceo/task` のEA出力=完全な日本語、プロジェクト全体を簡体字専用パターンで検査→**0件**。
- モデルティアリング維持(QA=mini)。
- **再起動なしで稼働**(採用時のみ run.py 生成で数十秒の自動再起動が入るが自動復帰)。

## 17. プロダクト運用メモ(新卒採用業務管理システム)

- `business/products/新卒採用業務管理システム`(owner=COO, status=planning, key_results=空)。
- フロー:プロダクト作成 → **企画(planning)** → EAが目的をヒアリング(Q1)で **CEO回答待ち** → 回答 → EAが KR・issue 生成 → CEO承認 → COO経由で開発(SOP `product_dev`) → イテレーション(v0.1.0→…)。
- UI導線:**左上「Products」パネル → プロダクトをクリック → Overviewの企画ボタン → 右に企画会話(1on1風)** で回答を入力。`POST /api/product/{slug}/planning` は既存会話があれば再開(二重起動しない設計)。

## 18. プランニングのエラー対応(`data.nodes is not iterable`)+ 企画の前進

- 症状:プロダクト企画の途中で `Error: data.nodes is not iterable`。
- 原因:`frontend/app.js` の `openTraceViewer` が `/api/projects/{id}/tree` を **`r.ok` 未チェック**で叩く。タスクツリーを持たないプロダクト(企画中)では backend が **HTTP 404**(`{"detail": "Task tree not found"}`、`nodes` 無し)を返すため、`for (const n of data.nodes)` が「not iterable」で落ちていた。
- 対策:`r.ok` をチェック(404は日本語メッセージ表示)し、`data.nodes || []` でガード。fork `ja` に commit `3b3e4ed`。**フロント変更はブラウザのハードリロード(Ctrl+F5)で反映**(サーバ再起動不要)。
- 企画フロー自体は正常:CEO回答を `POST /api/conversation/{conv_id}/message`(body `{text}`)で送信 → EA(加藤 葵)が**日本語で**受領し、次の質問 Q2(KRの期限)を返答。プロダクト企画は EA との**多段Q&A**(Q1目的 → Q2期限 → … → KR/issue 生成)で進む設計。
- 補足:エンドポイント整理 — プロジェクトのツリー取得 `GET /api/projects/{id}/tree`(無ければ404)、会話送信 `POST /api/conversation/{conv_id}/message`、プロダクト企画開始/再開 `POST /api/product/{slug}/planning`(既存会話があれば再開)。

## 19. 運用フローの整理 → 運用ランブック作成(2026-06-08)

- 目的:NORR の AI 組織で「プロダクトを作る」運用を、再現可能な手順書に整理。
- 方針(CEO 選択):**「まず1本→定常運用」** の両方を対象 / 関与粒度は **「フェーズ承認」**(企画・設計・実装・QA の節目にレビューゲート)。
- 1本目の題材:**中小企業向け採用管理システム(SME 向け ATS)**。
  - 既存の `business/products/新卒採用業務管理システム`(planning)とは**ターゲット/フレーミングが別**(新卒 vs 中小企業向け)。同一プロダクトを再スコープするか新規作成するかは要判断。
- 成果物:`docs/norr/operations-runbook.md`(運用ランブック)を作成。
  - Phase 0(起動・hot_reload 制御・コスト枠)。
  - Part A = 1本通し **5ゲート**(G1 企画 / G2 設計 / G3 実装[差分承認] / G4 QA・受け入れ / G5 出荷)。各ゲートに NORR ロスター担当・SOP・SME 向け ATS の具体仕様を割当。
  - Part B = 定常運用サイクル(Product 登録 → KR → Issue[P0/P1 自動 PJ 化] → Sprint → retro → KR 反映)。
  - 企画フェーズの実機導線(Products パネル → 企画ボタン → EA 多段 Q&A → KR/Issue 生成 → CEO 承認)と API(`POST /api/product/{slug}/planning` / `POST /api/conversation/{conv_id}/message` / `GET /api/projects/{id}/tree`)を反映。

## 20. SME 向け ATS の要件追加(総務兼任ペルソナ / ToDo自動生成 / 将来の分析)(2026-06-08)

- ペルソナ確定:**総務など他業務と兼任で採用を担当**する中小企業の担当者(専門性が浅く時間が乏しい)。
- コア価値の追加:情報を登録すると**選考状況に応じた「今日やる採用ToDo」を自動生成**し、判断せず手を動かすだけで対応漏れを防ぐ。
- 将来要件:蓄積データで**採用データ分析・傾向分析**(応募数推移・チャネル別効果・通過率/離脱ポイント・time-to-hire 傾向)→ **Phase 2**(非 MVP、ただし G2 設計で「初日からデータを取りこぼさない」記録設計をしておく)。
- ランブック反映:`docs/norr/operations-runbook.md` の G1(MVP に ToDo 自動生成を追加 / 分析を Phase 2 へ)・G2(イベント記録モデル + ToDo 生成ルール[ステージ×SLA] + 分析を見据えた構造化記録)・Part B(分析を P2 バックログに)を更新。
- Product 作成モーダル投入値(初期シード)も Objective / Owner(PdM 中村 結菜推奨)/ KR3〜4 本を確定。

## 19. git 反映状況の整理 & 本家への bugfix PR

- fork `nomhiro/OneManCompany` の **`ja` ブランチ**(= upstream/main + 5コミット、`origin/ja` に push 済み):
  - `ff5438e` `20a8686` `3417595` = i18n(中国語→日本語)、`3b3e4ed` = trace viewer の `data.nodes` ガード、`f51ce9f` = product 会話を UI で送信/表示する修正。
- i18n は中国語を置換するため本家には不適。**言語非依存の bugfix 2件だけ**を本家へ PR:
  - `upstream/main` 起点のクリーンブランチ `fix/product-planning-conversation-ui` を作成 → `git checkout ja -- frontend/app.js` で app.js の2修正のみ移植 → 404メッセージは英語化 → push。
  - **PR: [1mancompany/OneManCompany#404](https://github.com/1mancompany/OneManCompany/pull/404)**(trace viewer の `data.nodes` ガード + product 会話の UI 対応)。
- cross-fork PR はフォーク所有者で作る必要があり、`gh auth switch` で gh アクティブを `nomhiro` に切替えて作成(commit author は git config の KTC-HirokiNomura)。
- 作業後はローカルを `ja` に戻して日本語版を維持。
- 併せて fork 内で **`ja → main` の PR #1 を作成しマージ**(`gh pr merge ja --merge`)。fork の `main` が日本語版(merge commit `4d941fe`)になった。本家への bugfix PR #404 とは別管理。

(続く — 以降の作業はここに追記していく)
