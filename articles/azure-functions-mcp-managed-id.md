---
title: "Azure Functions MCP Binding を実践する　～Storage Account アクセスは ManagedIDで～"
emoji: "👻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "Functions", "mcp", "CosmosDB", "GitHubCopilot"]
published: false
---

# はじめに

生成AIの推論能力の向上と、Model Context Protocol（MCP）の登場により生成AIが動的にツール呼び出しできるようになっています。
生成AIに目的を与え、生成AIが能動的に目的のためにタスクを実行してくれます。

本記事では、Azure FunctionsをMCPサーバーとして活用し、研修講座のアンケートデータを動的に取得・分析するシステムの構築方法について解説します。
また、セキュリティベストプラクティスとして、Azure Functions から Azure Storage Account への接続は、Managed Identityを使用します。

### Model Context Protocol（MCP）とは

MCPは、AIモデルが外部のデータソースやツールと安全に連携するためのオープンスタンダードです。（現時点で）

AIが必要に応じて動的にツールを呼び出し、コンテキストに応じた適切なデータを取得できます。

# MCPを利用するシナリオ

ある企業が他社に対して、複数の研修講座を開催しています。
受講後には受講者からアンケートを収集しており、アンケート結果はデータベースに格納されているものとします。

**従来の課題**
- アンケートデータの集計を手作業で行う必要がある。
- 特定条件でのデータ抽出が煩雑（例：特定期間、特定講座、特定研修対象会社での絞り込み）
- 事前に決めた集計分析方法しか行えない。（動的にはしにくい）

**MCPによる解決**
- 必要な時に、自然言語で必要なだけのデータ集計・分析
- 用意したAPI（MCP ツール）を動的に呼び出す。

# システムアーキテクチャ

- **GitHub Copilot**: ユーザーの質問を解析して適切なMCPツールを呼び出す
- **Azure Functions**: MCPサーバーとして動作し、ツール呼び出しを処理
- **Azure Storage Account**: Azure Functionsのコードと設定、MCP Binding で Queue Storageを利用
  - セキュリティ強化のため、接続文字列やアクセスキーの代わりにManaged Identityを使用します。
- **Cosmos DB**: アンケートデータの保存
![](/images/azure-functions-mcp-managed-id/2025-09-07-19-46-19.png)


Managed Identity を利用するメリットはこれらがあります。StorageAccountのキー認証でもよいですが、キーの管理が不要になるため、セキュリティリスクを低減できます。

- **セキュリティ向上**: アクセスキーの管理が不要
- **自動ローテーション**: 資格情報の自動更新
- **最小権限の原則**: 必要最小限の権限のみ付与
- **監査証跡**: アクセスログの自動記録

---

# データ構成

アンケートデータは、以下のようなデータ構成で保存されているとします。
![](/images/azure-functions-mcp-managed-id/2025-09-07-19-52-55.png)

実際のサンプルデータの例はこちらです。

- アンケート結果（surveysコンテナー）
  ```json
  {
    "courseId": "d22fd304-a78f-4321-82ed-f5dccf178b09",
    "userId": "a10b2963-f48b-45a6-9dd2-588c5f053b90",
    "satisfactionRating": 1,
    "satisfactionComment": "インタラクションが少なく講義一方向で眠気を誘いました。 期待していた内容と異なりました。対象レベルの明確化が必要だと思います。",
    "difficultyRating": 3,
    "difficultyComment": "理論と実践が交互に現れ集中維持に寄与していました。 段階的に複雑性が増すが急激な跳ね上がりは無く安心して進めました。",
    "improvementRequest": ""
  }
  ```

- 講座情報（coursesコンテナー）
  ```json
  {
    "courseName": "ロジカルシンキング入門",
    "description": "MECEやピラミッド構造といったフレームワークを用いて、論理的に物事を考え、結論を導き出す方法を習得します。",
    "targetAudience": "若手社員、企画職",
    "targetCompany": "GHI通信株式会社",
    "conductedAt": "2024-05-15T09:00:00Z",
  }
  ```

- ユーザー情報（usersコンテナー）
  ```json
  {
    "userName": "斎藤 夏美",
    "companyName": "ABC商事株式会社",
    "departmentName": "法務部",
    "jobTitle": "スペシャリスト"
  }
  ```

# MCPツールの実装

MCPツールを用意するときには、どのようなシーンで利用されうるかを考えることが大事です。

研修講座（coursesコンテナー）に対しては、
- どのような講座があるか？
- 研修講座名をあいまい検索で探す
- 研修講座概要をあいまい検索で探す
- 特定の会社に向けた開催された研修講座はなにか？

アンケート結果（surveysコンテナー）に対しては、
- ある特定の研修講座（courseId）に対するアンケート結果を取得する
- ある特定のユーザー（userId）が回答したアンケート結果を取得する

ユーザー情報（usersコンテナー）に対しては、
- ある会社に所属するユーザーを取得する
- 特定のユーザIDのユーザー情報を取得する

### 利用可能なツール
上記の情報をもとに、以下のようなツールを用意することにします。

カテゴリ | toolName | 説明 | 引数
---------|----------|------|---------
Courses | list_all_courses | 研修講座情報（courses） 全件取得 | (なし)
Courses | search_courses_by_name | 研修講座名（courseName） 部分一致 | searchTerm, topK?
Courses | search_courses_by_description | 研修講座概要（description） 部分一致 | searchTerm, topK?
Courses | search_courses_by_company | 研修講座対象会社（targetCompany） 部分一致 | searchTerm, topK?
Surveys | query_surveys | 研修講座ID（courseId） か ユーザーID（userId） でアンケート取得 (どちらか/未指定はヘルプ) | courseId?, userId?, topK?
Users | get_users_by_ids | カンマ区切りユーザーID（userIds）で複数取得 | userIds ("id1,id2")
Users | get_users_by_company | 会社名（companyName）で一覧 | companyName, topK?


---

# Azureリソース払い出し

Azureポータルから以下のリソースを払い出します。
- リソースグループ
- Cosmos DB (Core SQL API)
- Azure Functions (Python)とAzure Storage Account
  - Azure Functions から Storage Account へのアクセスは、Managed Identityを利用します。

### リソースグループ

まずはリソースグループです。

![](/images/azure-functions-mcp-managed-id/2025-09-07-08-08-16.png)

### Cosmos DB

次にCosmosDBを払い出します。

![](/images/azure-functions-mcp-managed-id/2025-09-07-08-14-53.png)

検証目的なのでGeo-Redundantは不要とします。
![](/images/azure-functions-mcp-managed-id/2025-09-07-08-15-08.png)

ネットワーク設定はPublic Endpointのままとします。IP制限をする場合やPrivate Endpointを利用する場合は、適宜設定してください。
![](/images/azure-functions-mcp-managed-id/2025-09-07-08-15-25.png)

バックアップポリシーは、継続的バックアップにします。
![](/images/azure-functions-mcp-managed-id/2025-09-07-08-15-45.png)

![](/images/azure-functions-mcp-managed-id/2025-09-07-08-16-01.png)

データベースとコンテナー作成を作成します。
- データベース名：**course-surveys**
- コンテナー名
  - **surveys**
    - partition key: /id
  - **courses**
    - partition key: /id
  - **users**
    - partition key: /id

![](/images/azure-functions-mcp-managed-id/2025-09-07-08-29-33.png)

![](/images/azure-functions-mcp-managed-id/2025-09-07-08-30-37.png)

![](/images/azure-functions-mcp-managed-id/2025-09-07-08-32-20.png)

### Azure Functions

次にAzure Functionsです。
Hosting Planは、**Flex Consumption**にします。

![](/images/azure-functions-mcp-managed-id/2025-09-07-15-41-51.png)

検証目的なので、Zone Redundantは不要とします。
![](/images/azure-functions-mcp-managed-id/2025-09-07-15-42-33.png)

ストレージアカウントの設定です。新しく作成します。
![](/images/azure-functions-mcp-managed-id/2025-09-07-15-42-51.png)

パブリックネットワークアクセスは、**All networks**にします。IP制限やPrivate Endpointを利用する場合は、適宜設定してください。
![](/images/azure-functions-mcp-managed-id/2025-09-07-15-43-05.png)

Application insightsを有効にします。
![](/images/azure-functions-mcp-managed-id/2025-09-07-15-43-17.png)

認証設定です。キー認証ではなくManaged IDの認証を利用します。
各リソースごとに、ロール付与も自動で行われます。ManagedIDはシステム割り当てにします。
:::message
**しかし、MCP Binding を利用する場合、Storage Account に対するロール付与が足らないため、後ほど追加設定を行います。**
:::
![](/images/azure-functions-mcp-managed-id/2025-09-07-15-44-41.png)

Azure Functions の ManagedID に対し、追加で Storage Blob Data Contributor ロールを付与します。
:::message
Microsoft Learn のドキュメントには、Storage Queue Reader と Storage Queue Data Message Processor の2つを付与するように記載されていますが、これだけだと権限不足のエラーになりました。
そのため、Storage Blob Data Contributor を付与して強めなロール付与をしました。
:::
https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-bindings-mcp?pivots=programming-language-python#prerequisites
![](/images/azure-functions-mcp-managed-id/2025-09-07-20-17-46.png)

# Azure Functions の MCPツール実装
ソースコード全体は、GitHubにありますので良ければ参照ください。
https://github.com/nomhiro/azure-functions-mcp-managed-id

## 各MCPツールの実装

MCPツールの実装で最も大事なことはこれらです。
- **各MCPツールがどのようなときに呼び出されるべきツールなのか**
- **各MCPツールからどのようなデータが返されるのか**
- **各MCPツールの引数には何を設定すべきか**

:::message
これらが、生成AIがツールを呼び出すときに判断するときの材料です。**このコンテキストが不足していると、適切にツールが呼び出されません。**
:::

```python
import json
import azure.functions as func

# MCP トリガー (basic tools)
from functions.mcpTriggers.hello_time_mcp import (
	get_current_time_mcp,
)
from functions.mcpTriggers.course_search_mcp import (
	search_courses_by_name_mcp,
	search_courses_by_description_mcp,
	search_courses_by_company_mcp,
)
from functions.mcpTriggers.survey_query_mcp import (
	query_surveys_mcp,
)
from functions.mcpTriggers.course_list_mcp import (
	list_all_courses_mcp,
)
from functions.mcpTriggers.user_query_mcp import (
	get_users_by_ids_mcp,
	get_users_by_company_mcp,
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ---------------- MCP: Current Time ----------------
time_props = json.dumps([])
app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="get_current_time",
	description="現在の UTC 時刻を ISO8601 で返します。",
	toolProperties=time_props,
)(get_current_time_mcp)

# ---------------- MCP: List All Courses ----------------
list_all_courses_props = json.dumps([])
app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="list_all_courses",
	description="研修した講座の情報 （Id(courseId), courseName, description, targetCompany, conductedAt）を 最大1000件 取得します。courseIdやuserIdも返却されます。",
	toolProperties=list_all_courses_props,
)(list_all_courses_mcp)

# ---------------- MCP: Course Searches ----------------
search_common_props = json.dumps([
	{"propertyName": "searchTerm", "propertyType": "string", "description": "検索語 (必須)"},
	{"propertyName": "topK", "propertyType": "integer", "description": "最大返却件数 (default 5)"},
])

app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="search_courses_by_name",
	description="研修講座の内容を、講座名 (courseName) を対象にあいまい検索します。Id(courseId), courseName, description, targetCompany, conductedAt が返却されます。",
	toolProperties=search_common_props,
)(search_courses_by_name_mcp)

app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="search_courses_by_description",
	description="研修講座の内容を、講座概要 (description) を対象にあいまい検索します。Id(courseId), courseName, description, targetCompany, conductedAt が返却されます。",
	toolProperties=search_common_props,
)(search_courses_by_description_mcp)

app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="search_courses_by_company",
	description="研修講座の内容を、対象会社名 (targetCompany) を対象にあいまい検索します。Id(courseId), courseName, description, targetCompany, conductedAt が返却されます。",
	toolProperties=search_common_props,
)(search_courses_by_company_mcp)

# ---------------- MCP: Survey Query ----------------
survey_query_props = json.dumps([
	{"propertyName": "courseId", "propertyType": "string", "description": "講座ID (courses.id) 単一。courseIdのみで検索可能"},
	{"propertyName": "userId", "propertyType": "string", "description": "ユーザID (users.id) 単一。userIdのみで検索可能"},
	{"propertyName": "topK", "propertyType": "integer", "description": "最大取得件数 (default 20)"},
])
app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="query_surveys",
	description="courseId または userId をキーに 研修講座のアンケート結果を取得します。",
	toolProperties=survey_query_props,
)(query_surveys_mcp)

# ---------------- MCP: User Queries ----------------
users_by_ids_props = json.dumps([
	{"propertyName": "userIds", "propertyType": "string", "description": "取得したいユーザIDのカンマ区切り文字列 (例: id1,id2,id3)"}
])
app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="get_users_by_ids",
	description="研修を受講したユーザ情報（会社名、部署、役職）を取得します。userIds のリストに該当するユーザ情報を返却します。",
	toolProperties=users_by_ids_props,
)(get_users_by_ids_mcp)

users_by_company_props = json.dumps([
	{"propertyName": "companyName", "propertyType": "string", "description": "会社名 (完全一致)"},
	{"propertyName": "topK", "propertyType": "integer", "description": "最大返却件数 (default 200)"}
])
app.generic_trigger(
	arg_name="context",
	type="mcpToolTrigger",
	toolName="get_users_by_company",
	description="研修を受講したユーザ情報（会社名、部署、役職）を取得します。companyName に一致するユーザを userName の昇順で取得します。",
	toolProperties=users_by_company_props,
)(get_users_by_company_mcp)

__all__ = ["app"]
```

### CosmosDBからデータ取得する実装
CosmosDBからデータ取得する実装は、`course_list_mcp.py` と `course_search_mcp.py` にまとめています。
:::details コース情報を全取得するMCPTriggerの実装
```python
"""courses コンテナーの全件 (上限1000) を返す MCP ツール。

引数なしで呼び出し可能。サイズ肥大化防止のため 1000 件を超える場合は打ち切り、
"truncated": true を付加する。
"""
from typing import Any, Dict, List
import os
import logging
from azure.cosmos import CosmosClient, exceptions  # type: ignore
from ._common import parse_args, build_error, log_and_build_unhandled

_client = None
_container = None


def _init_cosmos():
    global _client, _container
    if _client is not None:
        return
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    db_name = os.getenv("COSMOS_DB", "course-surveys")
    container_name = os.getenv("COSMOS_COURSES_CONTAINER", "courses")
    if not endpoint or not key:
        logging.warning("[list_all_courses] COSMOS_ENDPOINT / COSMOS_KEY 未設定")
        return
    try:
        _client = CosmosClient(endpoint, credential=key)
        db = _client.get_database_client(db_name)
        _container = db.get_container_client(container_name)
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Cosmos 初期化失敗: {e}")
    except Exception as e:  # pragma: no cover
        logging.error(f"Cosmos 初期化予期せぬ失敗: {e}")


def list_all_courses_mcp(context):  # context は未使用（将来拡張用）
    try:
        # 引数があっても無視。将来的にフィルタ追加する際は parse_args を使う。
        parse_args(context)  # 解析だけ実行（副作用なし）
        _init_cosmos()
        if _container is None:
            return build_error("Cosmos コンテナー未初期化", kind="DependencyNotReady")

        query = "SELECT * FROM c"
        items: List[Dict[str, Any]] = []
        truncated = False
        try:
            for doc in _container.query_items(query=query, enable_cross_partition_query=True):
                items.append(doc)
                if len(items) >= 1000:  # 上限
                    truncated = True
                    break
        except exceptions.CosmosHttpResponseError as e:
            logging.warning(f"[list_all_courses] Cosmos クエリ失敗: {e}")
            return build_error("Cosmos クエリ失敗", details=str(e), kind="CosmosQueryError", extra={"query": query})

        return {
            "query": query,
            "count": len(items),
            "truncated": truncated,
            "results": items,
        }
    except Exception as e:  # pragma: no cover
        return log_and_build_unhandled(e, tool="list_all_courses")

__all__ = ["list_all_courses_mcp"]
```
:::

:::details コース情報を各フィールドに対してあいまい検索するMCPTriggerの実装
```python
import os
import logging
from typing import Any, Dict, List

from azure.cosmos import CosmosClient, exceptions  # type: ignore
from ._common import parse_args, build_error, log_and_build_unhandled

_client = None
_container = None


def _init_cosmos():
    """Lazy 初期化。"""
    global _client, _container
    if _client is not None:
        return
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    db_name = os.getenv("COSMOS_DB", "course-surveys")
    container_name = os.getenv("COSMOS_COURSES_CONTAINER", "courses")
    if not endpoint or not key:
        logging.warning("[course_search] COSMOS_ENDPOINT / COSMOS_KEY 未設定")
        return
    try:
        _client = CosmosClient(endpoint, credential=key)
        db = _client.get_database_client(db_name)
        _container = db.get_container_client(container_name)
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Cosmos 初期化失敗: {e}")
    except Exception as e:  # pragma: no cover
        logging.error(f"Cosmos 初期化予期せぬ失敗: {e}")


def _tokenize(term: str) -> List[str]:
    # シンプルに空白分割 (全角スペース対応)
    if not term:
        return []
    return [t for t in term.replace("\u3000", " ").split(" ") if t]


def _build_query(field: str, tokens: List[str]) -> str:
    # LOWER(c.field) に対して CONTAINS を AND 連結
    if not tokens:
        return f"SELECT * FROM c WHERE IS_DEFINED(c.{field})"
    conds = [f"CONTAINS(LOWER(c.{field}), @t{i})" for i, _ in enumerate(tokens)]
    where = " AND ".join(conds)
    return f"SELECT * FROM c WHERE {where}"


def _search_field(field: str, context):
    args = parse_args(context)
    # JSON でないプレーン文字列入力の場合 parse_args が {"raw": "..."} を返すため救済
    term = (args.get("searchTerm") or args.get("raw") or "").strip()
    if not term:
        return build_error("searchTerm は必須です", kind="ValidationError", extra={"field": "searchTerm"})
    top_k = int(args.get("topK") or 5)
    # 旧: maxScan / minScore は廃止
    tokens = _tokenize(term.lower())
    _init_cosmos()
    if _container is None:
        return build_error("Cosmos コンテナー未初期化", kind="DependencyNotReady")

    query = _build_query(field, tokens)
    params = [ {"name": f"@t{i}", "value": tok} for i, tok in enumerate(tokens) ]
    items: List[Dict[str, Any]] = []
    try:
        for doc in _container.query_items(query=query, parameters=params, enable_cross_partition_query=True):
            items.append(doc)
            if len(items) >= top_k * 3:  # 多少余分に取得して後で slice
                break
    except exceptions.CosmosHttpResponseError as e:
        logging.warning(f"[course_search] Cosmos クエリ失敗 field={field} term='{term}': {e}")
        return build_error("Cosmos クエリ失敗", details=str(e), kind="CosmosQueryError", extra={"query": query})
    except Exception as e:  # pragma: no cover
        return log_and_build_unhandled(e, tool=f"search_{field}")

    # 簡易スコア: 各トークンが含まれる割合 + 長さ比
    results = []
    for d in items:
        val = d.get(field)
        if not isinstance(val, str):
            continue
        lv = val.lower()
        if not all(tok in lv for tok in tokens):
            continue  # 保険
        token_hits = sum(1 for tok in tokens if tok in lv)
        length_bonus = min(len(term) / max(len(val), 1), 1.0)
        score = round((token_hits / max(len(tokens),1)) * 0.7 + length_bonus * 0.3, 4)
        snippet = val[:120] + ("..." if len(val) > 120 else "")
        results.append({
            "id": d.get("id"),
            "score": score,
            "fieldValue": val,
            "snippet": snippet,
            "doc": d,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    trimmed = results[:top_k]
    return {
        "query": term,
        "field": field,
        "tokens": tokens,
        "cosmosQuery": query,
        "matched": len(trimmed),
        "topK": top_k,
        "results": trimmed,
    }


def search_courses_by_name_mcp(context):
    return _search_field("courseName", context)


def search_courses_by_description_mcp(context):
    return _search_field("description", context)


def search_courses_by_company_mcp(context):
    return _search_field("targetCompany", context)

__all__ = [
    "search_courses_by_name_mcp",
    "search_courses_by_description_mcp",
    "search_courses_by_company_mcp",
]
```
:::

アンケート情報を取得する `survey_query_mcp.py`、ユーザー情報を取得する `user_get_mcp.py` も同様に実装しています。

:::details アンケート情報を取得するMCPTriggerの実装
```python
import os
import logging
from typing import Any, Dict, List

from azure.cosmos import CosmosClient, exceptions  # type: ignore
from ._common import parse_args, build_error, log_and_build_unhandled

_client = None
_container = None


def _init_cosmos():
    global _client, _container
    if _client is not None:
        return
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    db_name = os.getenv("COSMOS_DB", "course-surveys")
    container_name = os.getenv("COSMOS_SURVEYS_CONTAINER", "surveys")
    if not endpoint or not key:
        logging.warning("[query_surveys] COSMOS_ENDPOINT / COSMOS_KEY 未設定")
        return
    try:
        _client = CosmosClient(endpoint, credential=key)
        db = _client.get_database_client(db_name)
        _container = db.get_container_client(container_name)
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Cosmos 初期化失敗: {e}")
    except Exception as e:  # pragma: no cover
        logging.error(f"Cosmos 初期化予期せぬ失敗: {e}")


def _build_query(by_course: bool) -> str:
    if by_course:
        return "SELECT * FROM c WHERE c.courseId = @id"
    return "SELECT * FROM c WHERE c.userId = @id"


def query_surveys_mcp(context):
    """courseId か userId のどちらか 1 つで surveys を検索する MCP ツール。

    仕様:
      - 両方指定 → ValidationError
      - どちらも未指定 → ヘルプ (エラーにしない)
      - raw 文字列のみ → ヘルプ (usageExamples 付き)
      - topK 省略時 20
    """
    args = parse_args(context)
    course_id = (args.get("courseId") or "").strip()
    user_id = (args.get("userId") or "").strip()
    top_k = int(args.get("topK") or 20)

    # raw だけ来た場合 (JSON でキー不明)
    if not course_id and not user_id and args.get("raw"):
        return {
            "mode": None,
            "id": None,
            "query": None,
            "count": 0,
            "results": [],
            "info": "courseId か userId を JSON で指定してください",
            "raw": args.get("raw"),
            "usageExamples": [
                {"courseId": "<course-id>"},
                {"userId": "<user-id>"}
            ]
        }

    if course_id and user_id:
        return build_error("courseId と userId は同時指定できません", kind="ValidationError")

    if not course_id and not user_id:
        return {
            "mode": None,
            "id": None,
            "query": None,
            "count": 0,
            "results": [],
            "info": "courseId か userId のいずれかを指定するとアンケートを取得します",
            "usageExamples": [
                {"courseId": "<course-id>"},
                {"userId": "<user-id>"}
            ]
        }

    by_course = bool(course_id)
    target_id = course_id or user_id

    _init_cosmos()
    if _container is None:
        return build_error("Cosmos コンテナー未初期化", kind="DependencyNotReady")

    query = _build_query(by_course)
    params = [{"name": "@id", "value": target_id}]
    items: List[Dict[str, Any]] = []
    try:
        for doc in _container.query_items(query=query, parameters=params, enable_cross_partition_query=True):
            items.append(doc)
            if len(items) >= top_k:
                break
    except exceptions.CosmosHttpResponseError as e:
        logging.warning(f"[query_surveys] Cosmos クエリ失敗 id={target_id}: {e}")
        return build_error("Cosmos クエリ失敗", details=str(e), kind="CosmosQueryError", extra={"query": query, "id": target_id})
    except Exception as e:  # pragma: no cover
        return log_and_build_unhandled(e, tool="query_surveys")

    return {
        "mode": "courseId" if by_course else "userId",
        "id": target_id,
        "query": query,
        "count": len(items),
        "results": items,
    }

__all__ = ["query_surveys_mcp"]
```
:::

:::details ユーザー情報を取得するMCPTriggerの実装
```python
"""ユーザ情報取得用 MCP ツール群。

1. get_users_by_ids_mcp: userIds(配列/カンマ区切り文字列) からユーザドキュメントをまとめて取得。
2. get_users_by_company_mcp: companyName で同一企業のユーザ一覧を取得。

設計メモ:
- users コンテナー (環境変数: COSMOS_USERS_CONTAINER / 既定 'users') を参照。
- パーティションキーは companyName を想定。company 単位検索は単一パーティションなので高速。
- 複数 ID 取得は全パーティション跨ぎ → cross partition query 有効化。
- ヒント: ARRAY_CONTAINS(@ids, c.id) パターンで ID リストを一度に検索。
"""
from __future__ import annotations
from typing import Any, Dict, List
import os
import logging
from azure.cosmos import CosmosClient, exceptions  # type: ignore
from ._common import parse_args, build_error, log_and_build_unhandled

_client = None
_container = None


def _init_cosmos():
    global _client, _container
    if _client is not None:
        return
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    db_name = os.getenv("COSMOS_DB", "course-surveys")
    container_name = os.getenv("COSMOS_USERS_CONTAINER", "users")
    if not endpoint or not key:
        logging.warning("[user_query] COSMOS_ENDPOINT / COSMOS_KEY 未設定")
        return
    try:
        _client = CosmosClient(endpoint, credential=key)
        db = _client.get_database_client(db_name)
        _container = db.get_container_client(container_name)
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Cosmos 初期化失敗: {e}")
    except Exception as e:  # pragma: no cover
        logging.error(f"Cosmos 初期化予期せぬ失敗: {e}")


def _normalize_ids(raw) -> List[str]:
    """userIds のカンマ区切り文字列を配列に変換する。

    後方互換の list 入力サポートは削除済み。list / dict / その他型が来た場合は空リスト。
    例: "id1,id2 , id3" -> ["id1","id2","id3"]
    空や非文字列は []
    """
    if not isinstance(raw, str):
        return []
    raw = raw.strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def get_users_by_ids_mcp(context):
    try:
        args = parse_args(context)
        ids = _normalize_ids(args.get("userIds"))
        if not ids:
            # エラーではなく利用方法ガイド
            return {
                "query": None,
                "count": 0,
                "results": [],
                "info": "userIds にカンマ区切り文字列を指定してください (例: id1,id2,id3)",
                "usageExample": {"userIds": "id1,id2,id3"},
            }

        _init_cosmos()
        if _container is None:
            return build_error("Cosmos コンテナー未初期化", kind="DependencyNotReady")

        # ARRAY_CONTAINS(@ids, c.id) で一括取得
        query = "SELECT * FROM c WHERE ARRAY_CONTAINS(@ids, c.id)"
        params = [{"name": "@ids", "value": ids}]
        items: List[Dict[str, Any]] = []
        try:
            for doc in _container.query_items(query=query, parameters=params, enable_cross_partition_query=True):
                items.append(doc)
                if len(items) >= len(ids):  # 早期打ち切り（全ID 想定件数超過で停止）
                    break
        except exceptions.CosmosHttpResponseError as e:
            logging.warning(f"[get_users_by_ids] Cosmos クエリ失敗 ids={ids[:5]}..: {e}")
            return build_error("Cosmos クエリ失敗", details=str(e), kind="CosmosQueryError", extra={"query": query, "ids": ids[:10]})

        # 見つからなかった ID (差集合)
        found_ids = {d.get("id") for d in items}
        missing = [i for i in ids if i not in found_ids]
        return {
            "query": query,
            "requested": len(ids),
            "count": len(items),
            "missingIds": missing,
            "results": items,
        }
    except Exception as e:  # pragma: no cover
        return log_and_build_unhandled(e, tool="get_users_by_ids")


def get_users_by_company_mcp(context):
    try:
        args = parse_args(context)
        company = (args.get("companyName") or "").strip()
        top_k = int(args.get("topK") or 200)
        if not company:
            return {
                "query": None,
                "count": 0,
                "results": [],
                "info": "companyName を指定してください",
                "usageExample": {"companyName": "ABC商事株式会社"},
            }

        _init_cosmos()
        if _container is None:
            return build_error("Cosmos コンテナー未初期化", kind="DependencyNotReady")

        # パーティションキーが companyName である前提で単一パーティションクエリ: ORDER BY userName
        query = "SELECT * FROM c WHERE c.companyName = @company ORDER BY c.userName"
        params = [{"name": "@company", "value": company}]
        items: List[Dict[str, Any]] = []
        truncated = False
        try:
            # 単一パーティションなので enable_cross_partition_query 不要だが True でも可
            for doc in _container.query_items(query=query, parameters=params, partition_key=company):
                items.append(doc)
                if len(items) >= top_k:
                    truncated = True
                    break
        except exceptions.CosmosHttpResponseError as e:
            logging.warning(f"[get_users_by_company] Cosmos クエリ失敗 company={company}: {e}")
            return build_error("Cosmos クエリ失敗", details=str(e), kind="CosmosQueryError", extra={"query": query, "company": company})

        return {
            "query": query,
            "companyName": company,
            "count": len(items),
            "truncated": truncated,
            "results": items,
        }
    except Exception as e:  # pragma: no cover
        return log_and_build_unhandled(e, tool="get_users_by_company")


__all__ = [
    "get_users_by_ids_mcp",
    "get_users_by_company_mcp",
]
```
:::

Azure Functions 上で、以下のようにMCPTriggerと表示されて入れば準備完了です。
※テストのために、http_triggerやhello_world_mcpという関係ないトリガーも表示されています。
![](/images/azure-functions-mcp-managed-id/2025-09-07-20-40-26.png)

# GitHub Copilot からのMCP利用とアンケート分析

**Azure Functions MCP Trigger は、mcp_extension キーを headers に含めて呼び出す必要があります。**
Azure Portal からキー情報をコピーしておきましょう。
![](/images/azure-functions-mcp-managed-id/2025-09-07-20-42-28.png)

VSCodeを開き、`.vscode/mcp.json` ファイルを作成します。
```json
{
    "servers": {
        "course-survey": {
            "type": "sse",
            "url": "https://func-mcp-course-surveys.azurewebsites.net/runtime/webhooks/mcp/sse",
            "headers": {
                "x-functions-key": "コピーしたキーをここに貼り付け"
            }
        }
    }
}
```

Startボタンが表示されるので、Startすると以下のようにRunningになります。
![](/images/azure-functions-mcp-managed-id/2025-09-07-20-46-48.png)
また、ログに以下のように **Discovered xx tools** と表示されればOKです。
![](/images/azure-functions-mcp-managed-id/2025-09-07-20-47-32.png)

利用できるMCPツール一覧にこのように course-survey サーバーが表示されるはずです。
Build-In のツール群と、course-survey サーバーのツール群を選択しておきます。
![](/images/azure-functions-mcp-managed-id/2025-09-07-20-48-52.png)

https://youtu.be/o5niFmlRQ74

# まとめ
今回は、Azure Functions で MCPツールを実装し、Managed IdentityでCosmosDBにアクセスする方法を紹介しました。
MCPツールを設計するときのコツは、どのようなユースケースで使われる可能性があるかを想定することです。それによって、必要なMCPツールの実装は変わってきます。
今回のアンケート集計のような場合、**研修講座ごとに過去の満足度評価の平均を取得する** といったMCPツールがあると、より便利になるかもしれません。

それでは以上です。Azure Functionsは既存のデータベースや既存のAPIを活用してMCPツールを実装するのに非常に便利です。ぜひ試してみてください。

# 参考にしたドキュメント
https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-bindings-mcp?pivots=programming-language-python

