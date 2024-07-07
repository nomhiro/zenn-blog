---
title: "GraphRAG 第一弾 ~ Azureで動かしてみる ~ "
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "OpenAI", "GPT", "GraphRAG", "RAG"]
published: true
---

# はじめに

- GraphRagのGitHubリポジトリ
https://github.com/microsoft/graphrag

- GraphRag AcceleratorのGitHubリポジトリ
https://github.com/Azure-Samples/graphrag-accelerator


GraphRag Acceleratorは、GraphRagを動かすために、Azure上にデプロイする際に利用するIaC等のツール群が含まれます。また、後ほど試すnodebooksも含まれています。

# 環境構築

Acceleratorを利用して、GraphRagをAzure上にデプロイする手順を記載します。
デプロイするリソースは以下の構成です。
![](/images/graph_rag_ms/2024-07-07-18-22-54.png)

## 前提
- Dockerがインストールされていること。
※devcontainerで必要なツールがインストールされるため、Dockerがない場合は必要なツール群の個別インストールが必要。
https://github.com/Azure-Samples/graphrag-accelerator/blob/main/docs/DEPLOYMENT-GUIDE.md#prerequisites

- Azureのサブスクリプションに対し、以下2つのRBACが必要です。
  - Contributor
  - Role Based Access Control (RBAC) Administrator

- サブスクリプションに、リソースプロバイダーを登録されているか。
Azure Portal で確認できます。
  - Microsoft.OperationsManagement
  - Microsoft.AlertsManagement
![](/images/graph_rag_ms/2024-07-07-18-55-13.png)
![](/images/graph_rag_ms/2024-07-07-18-56-05.png)

## デプロイ手順

### Acceleratorのリポジトリをコンテナで開く

まず、GraphRag Acceleratorのリポジトリをクローンし、コンテナが動作している環境でVSCodeを開きます。
「Reopen Container」でコンテナを起動します。
![](/images/graph_rag_ms/2024-07-07-18-25-20.png)

::: message
※自分の環境の場合、devcontainer.jsonの31行目で「/.sshが存在しない」エラーになりました。
```json
"type=bind,source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh",
```

${localEnv:HOME}がなかったようなので、以下のように修正しました。
（本来はディレクトリパスを直接していするのは避けたいですが、とりあえず動作確認を進めたいので...）

```json
"type=bind,source=C:/Users/{自身のローカルアカウント名}/.ssh,target=/home/vscode/.ssh",
```
:::

### Bicep実行前の事前準備

#### Azure OpenAI Serviceをデプロイ

OpenAIリソース払い出し手順は割愛します。こちらを参考にしてください。
https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal

GPTモデルは、以下の2つをデプロイしておきます。※デプロイ名=モデル名にしておきましょう。
- GPT-4o
- text-embedding-ada-002

![](/images/graph_rag_ms/2024-07-07-19-12-02.png)

#### Azureにログイン

AzureCLIでAzureにログインし、サブスクリプションを選択

```bash
az login
az account show
z account set --subscription "<サブスクリプション名> or <サブスクリプションID>"
```

#### リソースグループを作成

AzureCLIでリソースグループを作成します。※AzurePortalでも可

```bash
az group create --name <リソースグループ名> --location <リージョン>
```
例）az group create --name rg-graph-rag --location JapanEast

### Bicepによるデプロイ

::: details Bicepコードの解説
- 変数定義 (var roles): 特定のAzureロール定義に対するリソースIDをマッピングする変数を定義しています。これらのロールは後でリソースに割り当てられます。

- Log Analyticsワークスペース (module log): Azure Monitorの一部であるLog Analyticsワークスペースを作成します。このモジュールは、ログデータの収集、検索、および可視化を可能にします。

- Azure Kubernetes Service (AKS) (module aks): AKSクラスターをデプロイします。このモジュールは、クラスター名、地域、SSH公開鍵、およびLog AnalyticsワークスペースIDなどのパラメータを指定します。

- Azure Cosmos DB (module cosmosdb): NoSQLデータベースサービスであるCosmos DBのインスタンスを作成します。このモジュールは、データベース名、地域、ネットワークアクセス設定などを定義します。

- Azure Cognitive Search (module aiSearch): 検索サービスのインスタンスをデプロイします。このモジュールは、サービス名、地域、ネットワークアクセス設定、およびロール割り当てを定義します。

- Azure Storageアカウント (module storage): ストレージアカウントを作成します。このモジュールは、アカウント名、地域、ネットワークアクセス設定、タグ、ロール割り当て、削除ポリシーなどを定義します。

- Azure API Management (APIM) (module apim): API管理サービスのインスタンスをデプロイします。このモジュールは、サービス名、地域、SKU、パブリッシャーの詳細などを定義します。

- Workload Identity (module workloadIdentity): ワークロードアイデンティティを使用して、Azureリソースにアクセスするためのセキュアな方法を提供します。

- Private DNS Zone (module privateDnsZone): プライベートDNSゾーンを作成し、特定の仮想ネットワークに関連付けます。

- Private Endpoint (module *PrivateEndpoint): 特定のAzureリソース（Cosmos DB、Blob Storage、Queue Storage、AI Search、Private Link Scope）に対するプライベートエンドポイントを作成します。これにより、プライベートネットワークからこれらのサービスにアクセスできます。

- 出力 (output): デプロイメントの結果として得られる重要な情報（例：リソース名、エンドポイントURL、IDなど）を出力します。
:::

上記で作成したリソースをBicepのパラーメータファイルに設定します。
./infra/deploy.parameters.jsonを修正します。

```json
{
  "GRAPHRAG_API_BASE": "OpenAIのエンドポイント",
  "GRAPHRAG_API_VERSION": "OpenAIのAPIVersion",
  "GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME": "embeddingモデルのデプロイ名",
  "GRAPHRAG_EMBEDDING_MODEL": "embeddingモデル名",
  "GRAPHRAG_LLM_DEPLOYMENT_NAME": "GPT-4oのデプロイ名",
  "GRAPHRAG_LLM_MODEL": "GPT-4oモデル名",
  "LOCATION": "GraphRAGリソースをデプロイするリージョン",
  "RESOURCE_GROUP": "リソースグループ名"
}
```

:::details ※以下の任意パラメータもあります。必要に応じて設定してください。
- GRAPHRAG_COGNITIVE_SERVICES_ENDPOINT
  - CognitiveServiceのエンドポイント
- APIM_NAME
  - APIManagementのホスト名
- RESOURCE_BASE_NAME
  - すべてのAzureリソースに付与されるプレフィックス
- AISEARCH_ENDPOINT_SUFFIX
  - AISearchエンドポイントのサフィックス
- AISEARCH_AUDIENCE
  - AISearchする対象ユーザ
- REPORTERS
  - ログタイプ　※指定しない場合、ログはAzureStorageのファイルとAKSコンソールに出力される。
:::


infraディレクトリに移動し、以下のコマンドを実行してリソースをデプロイ

```bash
cd infra
bash deploy.sh -p deploy.parameters.json
```

デプロイ結果がコンソールに出力され、以下リソース群が作成されます。
- Container Registry
- 

:::message
自分の環境では、deploy.shの実行時に以下エラーになりました。deploy.sh スクリプトが Windows 形式の改行コード (CRLF) を使用しているために発生しています。
```bash
bash deploy.sh -p deploy.parameters.json
deploy.sh: line 4: $'\r': command not found
deploy.sh: line 6: $'\r': command not found
deploy.sh: line 8: $'\r': command not found
deploy.sh: line 17: $'\r': command not found
deploy.sh: line 28: $'\r': command not found
deploy.sh: line 30: syntax error near unexpected token `$'{\r''
'eploy.sh: line 30: `exitIfCommandFailed () {
```

ファイル内の Windows 形式の改行コード (CRLF) を Linux 形式の改行コード (LF) に変換します。
```bash
sed -i 's/\r$//' deploy.sh
```
:::

以下のようにコンソールに出力されていれば、デプロイ成功です。
  
```bash
SUCCESS: GraphRAG deployment to resource group rg-graph-rag complete
```

# GraphRAGを試してみる

./notebooksディレクトリにあるQuickStartを実行してみます。

Pythonライブラリのインストール

::: details コード
```bash
! pip install devtools python-magic requests tqdm
```
:::

![](/images/graph_rag_ms/2024-07-07-21-28-29.png)

![](/images/graph_rag_ms/2024-07-07-21-29-12.png)

APIサブスクリプション・キーを設定
※AzurePortalのAPIManagementの画面 -> APIs -> サブスクリプション -> Build-in all-access subscription -> 主キー

::: details コード
```python
ocp_apim_subscription_key = getpass.getpass(
    "Enter the subscription key to the GraphRag APIM:"
)

"""
"Ocp-Apim-Subscription-Key": 
    This is a custom HTTP header used by Azure API Management service (APIM) to 
    authenticate API requests. The value for this key should be set to the subscription 
    key provided by the Azure APIM instance in your GraphRAG resource group.
"""
headers = {"Ocp-Apim-Subscription-Key": ocp_apim_subscription_key}
```
:::

![](/images/graph_rag_ms/2024-07-07-21-33-48.png)

wikiの情報を取得するPythonコードを修正します。
日本語のWikipediaの情報を取得するように、14行目に以下を追加
```python
wikipedia.set_lang("ja")
```

取得するWikipediaの情報を以下のように修正します。コード内のus_statesをjp_aichiに変更します。
```python
jp_aichi = [
    "名古屋城",
    "織田信長",
    "織田信秀",
    "明智光秀",
    "尾張国",
]
```

![](/images/graph_rag_ms/2024-07-07-21-54-47.png)

testdataディレクトリにtxtファイルが作成されていることを確認します。
![](/images/graph_rag_ms/2024-07-07-21-54-58.png)

GraphDBにするデータのディレクトリ設定と、APIManagementのエンドポイントを設定
```python
file_directory = "textファイルのディレクトリ"
storage_name = "textファイルがアップロードされるBlobコンテナ名"
index_name = "AISearchのIndex名"
endpoint = "APIManagementのエンドポイント"
```

![](/images/graph_rag_ms/2024-07-07-22-00-38.png)

![](/images/graph_rag_ms/2024-07-07-22-00-53.png)

ファイルをBlobStorageにアップロードする。

![](/images/graph_rag_ms/2024-07-07-22-01-47.png)

AISearchのIndexを作成する。

![](/images/graph_rag_ms/2024-07-07-22-06-19.png)

IndexweによるIndex構築が完了しているか、確認する。
以下はまだ実行中。
![](/images/graph_rag_ms/2024-07-07-22-07-33.png)
completeになるまで待って再実行します。

completeになりました。　※completeになるまで、30分近くかかりました。
![](/images/graph_rag_ms/2024-07-07-23-38-36.png)

作成されたIndexにクエリしてみます。
**クエリの種類は「Global Query」と「Local Query」の2種類があります。**

## Global Query

まずは「Global Query」を実行します。
- Global Queryは、データセット全体にクエリを実行するモードのようです。
- **データセット全体の理解を必要とする質問に対して有効。**
- 一方で、データセット全体にクエリを実行するため、処理に時間がかかる。

日本語で回答してほしいので、クエリを日本語に変更します。
```python
global_response = global_search(
    index_name=index_name, query="データ全体のトピックを要約して。"
)
```

実行すると以下のように回答が返ってきました。**登録した複数のファイルを、ファイル横断で要約してくれています。**
実行時間は45sです。
```markdown
## データセットのトピック要約

### 織田信長と織田氏

織田信長は戦国時代の著名な大名であり、織田氏のリーダーとして日本史において重要な役割を果たしました。彼の軍事的な才能と革新的な戦略は、数々の戦いで勝利を収める要因となりました。特に、桶狭間の戦いでの今川義元の打倒や、伊勢侵攻と稲葉山城の攻略が彼の権力を確立する上で重要でした [Data: Reports (131, 186, 82, 244, 90, 220, 169, 80, +more)]。信長の最期は本能寺の変で明智光秀に裏切られたことで幕を閉じましたが、この事件は豊臣秀吉の台頭を促す結果となりました [Data: Reports (91, 119)]。

### 名古屋城とその歴史的構造物

名古屋城は、特に第二次世界大戦中の名古屋空襲で大きな被害を受けた後、戦後の復興努力が続けられてきました。城の主要な構造物には、本丸御殿や大天守、小天守が含まれ、これらは文化的および歴史的に重要な資産とされています [Data: Reports (45, 206, 49, 202, 196, 67, 44, +more)]。また、名古屋城の建設には池田輝政などの重要な人物が関与しており、その文化的意義が強調されています [Data: Reports (104)]。

### 豊臣秀吉と日本の統一

豊臣秀吉は、信長の死後に台頭し、日本の統一を果たした重要な人物です。彼の軍事キャンペーンや文化的貢献、戦略的な同盟関係は、日本史において大きな影響を与えました [Data: Reports (167)]。

### 戦国時代のその他の重要な人物と出来事

戦国時代には、他にも多くの重要な人物と出来事が存在しました。例えば、徳川家康と石田三成が中心となった関ヶ原の戦いは、徳川幕府の成立に繋がる決定的な戦いでした [Data: Reports (229)]。また、武田信玄や浅井長政などの大名も、地域の統治と軍事戦略において重要な役割を果たしました [Data: Reports (241, 192)]。

### 文化的および宗教的な影響

織田信長の時代には、宗教的な対立や文化的な変革も多く見られました。例えば、安土宗論では浄土宗と日蓮宗の対立があり、信長の影響下で日蓮宗が抑圧されました [Data: Reports (173)]。また、信長とローマ教皇グレゴリウス13世との文化交流も行われました [Data: Reports (71)]。

### その他の歴史的な場所と出来事

データセットには、名古屋城以外にも多くの歴史的な場所や出来事が含まれています。例えば、熱田神宮や長島一向一揆の鎮圧などが挙げられます [Data: Reports (211, 234)]。また、名古屋市議会と木造復元プロジェクトなど、現代における歴史的建造物の保存活動も取り上げられています [Data: Reports (205)]。

このように、データセットは戦国時代から現代に至るまでの日本の歴史と文化に関する多岐にわたるトピックを網羅しています。
CPU times: user 58.5 ms, sys: 27.8 ms, total: 86.4 ms
Wall time: 44.9 s
```

## Local Query

次に「Local Query」を実行します。
- **Local Queryは、文書に記載されている特定の情報を理解する必要がある、焦点を絞った質問に有効です。**
- ※なぜLocalという名前なんだろう。なんだか分かりにくい...

クエリを以下に変更して実行します。
```python
local_response = local_search(
    index_name=index_name, query="明智光秀と織田信秀の関係性は？"
)
```

実行すると以下のように回答が返ってきました。
クエリを回答するためには、ファイル横断で情報を理解する必要がありますが、回答の内容は間違っていません。
実行時間は20.6sです。Gloal Queryよりも早いです。検索してクエリに類似するデータのみを使って推論すしているので、処理が早いのだと思います。
```markdown
# 明智光秀と織田信秀の関係性

## 概要

明智光秀と織田信秀の関係性については、直接的なつながりは記録されていませんが、彼らの家族や周囲の人物を通じて間接的な関係が見られます。以下に、彼らの関係性に関連する情報をまとめます。

## 明智光秀の背景

明智光秀は、戦国時代の武将であり、織田信長に仕えたことで知られています。彼の養父は明智光綱（光隆）であり、光秀は養子として育てられました [Data: Entities (130); Relationships (12)]。

## 織田信秀の背景

織田信秀は、織田信長の父であり、尾張国の有力な大名でした。信秀は織田家の勢力を拡大し、信長の基盤を築いた人物です [Data: Entities (2584, 2583); Relationships (2799, 2798)]。

## 間接的な関係

### 家族関係

- **織田信長と明智光秀**: 織田信長は信秀の息子であり、明智光秀は信長に仕えた家臣です。このため、信秀と光秀の間接的な関係は、信長を通じて形成されました [Data: Relationships (835, 837)]。

- **秀孝と信秀**: 秀孝は信秀の息子であり、信長の兄弟です。秀孝の存在も、信秀と光秀の間接的な関係を示しています [Data: Entities (2583); Relationships (2799, 3659)]。

### 歴史的背景

- **織田家と明智家の関係**: 織田家と明智家は、戦国時代の日本において重要な役割を果たしました。信秀の時代には、織田家の勢力拡大が進み、信長の時代にはさらに強固なものとなりました。光秀はその中で重要な役割を果たし、最終的には本能寺の変を引き起こすこととなります [Data: Entities (2824); Relationships (1101)]。
...

明智光秀と織田信秀の関係性は、直接的なものではなく、主に織田信長を通じた間接的な関係に基づいています。信秀の息子である信長に仕えた光秀の存在が、両者の間接的なつながりを示しています。信秀の影響力と光秀の行動は、戦国時代の日本の歴史において重要な要素となっています。
CPU times: user 37.6 ms, sys: 6.19 ms, total: 43.8 ms
Wall time: 20.6 s
```

## 実行結果を確認する
Global QueryもLocal Queryも、回答の中には「Entity」と「Relation」のIDが含まれています。
```
例） [Data: Entities (2824); Relationships (1101)]
```
クエリに対して、EntityとRelationを取得し（RAG）、生成AIの回答に使っているようです。
どの回答にどの情報が使ったかを追うことができそうです。

#### Gloabl Queryで、特定の情報について聞いてみる
気になったので、試しにGlobal Queryで特定の情報について聞いてみます。
```python
global_response = global_search(
    index_name=index_name, query="明智光秀と織田信秀の関係性は？"
)
```

```markdown
### 明智光秀と織田信秀の関係性

明智光秀と織田信秀の直接的な関係についての具体的な記述は、提供されたデータには含まれていません。しかし、いくつかの重要な点を考慮することで、彼らの間接的な関係性について理解を深めることができます。

#### 織田信秀の影響

織田信秀は織田信長の父であり、尾張国の有力な大名でした。信秀の死後、信長が家督を継ぎ、明智光秀を含む多くの家臣が信長に仕えることになりました [Data: Reports (136, 167, 241, 173, 75)]。このことから、信秀の時代における政治的・軍事的な動きが、明智家に影響を与えた可能性があります [Data: Reports (100)]。

#### 明智光秀と織田信長の関係

明智光秀は織田信長の家臣であり、信長の命令で多くの軍事作戦に参加し、信長の信頼を得ていました [Data: Reports (136, 167, 241, 173, 75)]。しかし、彼らの関係は複雑で、協力と対立の両面がありました。最終的に光秀は信長を裏切り、本能寺の変で信長を暗殺しました [Data: Reports (91)]。

#### まとめ

明智光秀と織田信秀の直接的な関係についての具体的な情報は提供されていませんが、信秀の影響を受けた可能性はあります。光秀が信長に仕えていたことから、信秀の時代の政治的・軍事的な動きが間接的に光秀に影響を与えたと考えられます [Data: Reports (136, 167, 241, 173, 75, 100)]。
CPU times: user 68.7 ms, sys: 1.18 ms, total: 69.9 ms
Wall time: 19.8 s
```

Local Queryの時よりも、おおざっぱな回答になっています。おそらくですが、GlobalQueryではデータセットを検索せず、データセット全体を使ってOpenAIで推論を行われたことで、回答に必要がない余分な情報が含まれるので、おおざっぱな回答になったと思われます。


# まとめ
まず第一弾として、Microsoft Researchから提供されたGraphRAGを動かせるように環境構築しました。
Acceleratorが用意されているため、構築は非常に楽です。
txtデータ使ってIndexを構築し、2種類のクエリ「Global Query」と「Local Query」を実行し、それぞれの結果を確認しました。

動作確認をしただけで、ナレッジグラフを構築する部分の処理詳細や、GlobalQueryとLocalQueryがどのような処理で実行されているのか、まだ追えていませんので、そちらはいずれ整理します。

**また、このようなGraphRAGを使うときに課題だと感じていたのが、元データが追加/更新/削除された時のGraphデータの追従です。** この点についても、今後検証していきたいと思います。

次回の第二弾では、GraphRAGにAPIが用意されているためそれらを利用して、GraphRAGの動きを確認してみます。