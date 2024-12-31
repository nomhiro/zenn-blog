---
title: "GraphRAGが進化？ AzureAISearchと連携しGraphRAG1.0でナレッジグラフを運用しよう"
emoji: "😺"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["GraphRAG", "OpenAI", "RAG"]
published: false
---

# GraphRAG 1.0 の更新まとめ
Microsoftからの公式アナウンスはこちらです。
https://www.microsoft.com/en-us/research/blog/moving-to-graphrag-1-0-streamlining-ergonomics-for-developers-and-users/?msockid=1d82c10dd1eb639f3fbfd40fd0ef6238

### GraphRAG利用開始時のセットアップが簡単に
いままでは環境変数の設定が必要で、設定できるオプションが多かったため設定が面倒でした。
1.0のUpdateでは init コマンドが用意され、GraphRAGに必要な設定がそろったsettings.ymlファイルが生成されるようになりました。

### CLIの改善
いままでのCLIは、デモ用として用意されていただけでした。
1.0のUpdateでは、GraphRAGを操作するための機能が増えました。
https://microsoft.github.io/graphrag/cli/

これらのコマンドが用意されました。
- **設定ファイルの作成**
  - > init [OPTIONS]
- **プロンプトチューニング（自動）**
登録するデータをもとにして、ナレッジグラフを構成するためのプロンプトをチューニングします。
  - > prompt-tune [OPTIONS]
- **ナレッジグラフ インデックスの作成**
  - > index [OPTIONS]
- **ナレッジグラフ インデックスへのクエリ**
  - > query [OPTIONS]
- **ナレッジグラフ インデックスのアップデート**
  - > update [OPTIONS]

### APIレイヤーの追加

### データモデルの簡略化
いままでは研究目的で、ナレッジデータ化のための中間データが多く、使われていないデータが多かったようです。
1.0のUpdateでは、冗長であったり未使用なフィールドが削除されたことで、データモデルが簡略化されました。

### ベクトルストア
いままでは、ナレッジデータのインデックス作成後に、Parquetファイル内にすべてのベクトル値を保存していました。
1.0のUpdateでは、インデックス作成時にベクトル値は別のベクトルストアに格納するように修正されました。サイズの大きいベクトル値を含むファイルをロードする必要がなくなったため、クエリに対する応答時間が向上します。Parquetファイルのディスク容量は80%削減され、総ディスクスペースは43%削減されました。
ベクトルストアとしては、LanceDBとAzureAISearchがサポート対象です。※デフォルトはLanceDBです。

### データの更新
いままでは、一度作成したナレッジデータに対してナレッジデータにしたいデータを追加するためには、データセット全体を一から再度インデックス作成する必要がありました。
1.0のUpdateでは、既存のインデックスと追加データの差分が計算され、更新分を既存のインデックスにマージすることができるようになりました。


# 今後のロードマップ
LazyGraphRAGの考え方もGraphRAGに取り込む予定のようです。
LazyGraphRAGとは、LLMの使用を避けることで、インデックス作成のコストを避ける手法です。
https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/

### LazyGraphRAGの概要
GraphRAGの思想から、LLMの試用を可能な限り避けます。その代わりにクエリの工夫や、回答に使うデータをフィルターします。
前提として、グラフデータには、コミュニティ（テキストチャンクのグループ。テーマやトピックで分かれる）の階層構造があります。

- インデックス作成
  - 自然言語処理を使い、文章から重要な名詞（概念）を抽出します。
  - 次にその概念に近い用語（共起）を抽出します。
  - 抽出された概念と共起の名詞群をもとに、意味のあるネットワークグラフを作成します。似た概念の用語が多く出現するということは、その概念に関する文章だよね。というアプローチですね。
  - 作成されたグラフデータを、グループに分けて階層的な構造にします。グラフデータに対して、テーマやトピックが明確にできます。
- グラフデータの要約は行いません。（LLMの試用を避ける）
- 拡張クエリに変換
  - LLMを試用して、サブクエリを生成します。
  - さらに、概念グラフデータに一致するサブクエリに絞ります。　※概念グラフデータにないなら、そもそもクエリする必要ないよね。というアプローチですね。
  - サブクエリを結合して拡張クエリにします。
- クエリのマッチング
  - 各サブクエリに対して、インデックスのテキストチャンクを類似度でライク付けします。
  - 上記k個のテクストチャンクのランクをもとに、グラフのコミュニティをランク付けします。
  - LLMを使い、ランク付けされたコミュニティから上位k個のテキストチャンクの関連性を評価します。
- 回答のためのマップデータ作成
  - 各サブクエリに対して、関連するテキストチャンクから概念サブグラフを構築します。
  - 概念サブグラフに対してコミュニティデータを適用し、関連するテキストチャンクをグループ化します。※関連する情報がコミュニティにまとまります。
  - LLMを試用して、コミュニティからサブクエリに関連するデータを抽出します
  - 抽出された関連データをランク付けして、フィルタリングします。
- LLMを使い、マップデータをもとに拡張クエリに回答します。

# GraphRAGのインデックスの構成

## ナレッジモデルのデータ
- **Document**
  - ナレッジグラフ登録対象のドキュメント。csvまたは.txtファイルの個々の行を指す
- **TextUnit**
  - ドキュメントをチャンク化したもの。
- **Entity**
  - TextUnitから抽出されたエンティティ。※ユーザ、場所、イベントなど。
- **Relationship**
  - 2つのEntity間の関係性を表す。
- **Covariate**（共変量）
  - Entityに対する追加情報
- **Community**
  - EntityとRealationshitのグラフが作成されたあとに、まとまりごとに階層的にグループ化（クラスタリング）したもの。
- **Node**
  - クラスタリングしたEntityと、グラフビューのレイアウト情報を含むテーブル。

## ナレッジグラフにするワークフロー
![](/images/graphrag-1_0/2024-12-21-22-10-51.png)

#### Phase1：TextUnitの構成
入力DocumentをTextUnitにチャンク化します。
- Chunk化のサイズはデフォルト300トークン。設定でカスタマイズ可能。
- チャンクが大きいほど、処理時間は短縮されるが、質問に対する出力の関連度が下がる可能性がある。

#### Phase2：Graphの抽出
TextUnitを分析し、Graph構造（Entity、Relation、Claim）を抽出します。
1. **EntityとRelationの抽出**
   - LLMを使い、TextUnitからEntity（名前、場所、イベント、説明など）を抽出し、 SourceとTarget、その説明を含むRelationを抽出する。**Subgraph-per-TextUnit**と定義されている。
   - Subgraph横断で、同じ名前とタイプのEntityは、説明を配列に入れることでマージされる。同じSourceとTargetを持つRelationは、説明を配列に入れることでマージされる。
2. **EntityとRelationの要約**
   - EntityとRelationごとに、それぞれの説明の配列をもとにLLMに要約させる。
3. **Claim抽出**　※デフォルトではClaim抽出は実施されない。機能を有効にする場合はチューニングが必要。
   - TextUnitからEntityに対する追加情報として、Claimを抽出する。（Covariate(共変量)と呼ばれる)

#### Phase3：Graphデータの拡張
EntityとRelationのグラフデータをCommunity構造にする（グループ化する）

1. **コミュニティの検出**
   - コミュニティサイズの閾値に達するまで、再帰的にコミュニティクラスタリングを実行する。
2. **Graphのベクトル表現（埋め込み）**
   - Node2Vecアルゴリズムを用い、Graphのベクトル表現を生成する。
   - クエリフェーズで、関連する概念を検索するために使われる。
3. **GraphテーブルにExport**
   - 最終的なEntity Table と Relationship Table

#### Phase4：Communityの要約
EntityとRelationshipのGraph、EntityのCommunity階層、およびNode2Vec埋め込みを基に、各Communityのレポートを生成し、要約します。

1. **Communityレポートの生成**
   - LLMを使用して、各Communityの要約を生成します。これらのレポートには、Communityの概要と、Communityのサブ構造内の主要なEntity、Relationship、およびClaimが含まれます。
2. **Communityレポートの要約**
   - 各CommunityレポートをLLMで要約し、簡潔な使用のための要約を生成します。
3. **Communityの埋め込み**
   - Communityレポート、Communityレポートの要約、およびCommunityレポートのタイトルのテキスト埋め込みを生成し、Communityのベクトル表現を作成します。
4. **CommunityテーブルのExport**
   - CommunityとCommunityレポートのテーブルをExportします。

#### Phase 5：Document処理
ナレッジモデルのためのDocumentsテーブルを作成します。

1. **追加フィールド (CSV Only)**
   - ワークフローがCSVデータで動作している場合、Documents出力に追加フィールドを追加するように設定できます。
2. **DocumentをTextUnitにリンク**
   - 各ドキュメントを最初のフェーズで作成されたテキストユニットにリンクします。
   ※どのドキュメントがどのテキストユニットに関連しているかを理解することができます。
3. **Documentの埋め込み（ベクトル化）**
   - ドキュメントのベクトル表現を生成します。ドキュメントを重複しないチャンクに再分割し、各チャンクの埋め込みを生成します。　
   ※ドキュメント間の暗黙的な関係を理解し、ドキュメントのネットワーク表現を生成するのに役立ちます。
4. **Documents Table Emission**
   - Documentsテーブルをナレッジモデルにエクスポートします。

#### Phase 6：グラフデータをネットワーク図に可視化
Graphをネットワーク可視化するためのステップです。

1. **Umap Documents**
   - DocumentのGraphに対してUMAP次元削減を実行し、Graphの2次元表現を生成します。
   これにより、Graphを2次元空間で視覚化し、Graph内のノード間の関係を理解できます。
2. **Umap Entities**
   - EntityのGraphに対してUMAP次元削減を実行し、Graphの2次元表現を生成します。
   これにより、Graphを2次元空間で視覚化し、Graph内のノード間の関係を理解できます。
3. **Nodes Table Emission**
   - UMAP埋め込みをNodes Tableとしてエクスポートします。このテーブルの行には、ノードがDocumentかEntityかを示す識別子と、UMAP座標が含まれます。


# まずは使ってみましょう
大事なのは試すデータを何にするかですね。

GraphRAGはPythonのライブラリとして提供されます。
GraphRAGを試す際にAcceleratorパッケージが用意されています。
https://github.com/Azure-Samples/graphrag-accelerator

## 事前準備
Acceleratorで用意されているDecContainerの設定でセットアップします。
「Reopen in Container」でコンテナを作って開きます。
![](/images/graphrag-1_0/2024-12-22-11-01-30.png)

コンテナが起動すると、entirypoint.shが実行され、Pythonの必要なモジュールがインストールされます。
![](/images/graphrag-1_0/2024-12-22-11-19-33.png)

## デプロイ
infra フォルダの deploy.parameters.json に設定を記述します。
```json
{
  "GRAPHRAG_API_BASE": "https://aoai-poc-eastus2-01.openai.azure.com/",
  "GRAPHRAG_API_VERSION": "2024-10-01-preview",
  "GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME": "text-embedding-3-small",
  "GRAPHRAG_EMBEDDING_MODEL": "text-embedding-3-small",
  "GRAPHRAG_LLM_DEPLOYMENT_NAME": "gpt-4o",
  "GRAPHRAG_LLM_MODEL": "gpt-4o",
  "LOCATION": "eastus2",
  "RESOURCE_GROUP": "rg-graphrag"
}
```

Azureにログインしてサブスクリプションを設定します。
```bash
az login
az account show
az account set --subscription "<subscription_name> or <subscription id>"
```

infra フォルダの deploy.sh を実行します。
```bash
bash deploy.sh -p deploy.parameters.json
```

Successfull !!!
![](/images/graphrag-1_0/2024-12-22-18-45-19.png)

以下の構成図でリソースがデプロイされます。
![](/images/graphrag-1_0/2024-12-22-18-50-28.png)

## Jypyter Notebookで試します
notebookos フォルダの1-Quickstart.ipynb を実行していきます。

### 事前設定
以下を実行すると、VSCodeから入力が求められるので、API ManagementのAPI subscription keyを入力します。
```python
ocp_apim_subscription_key = getpass.getpass(
  "API ManagementのAPI subscription keyを設定"
)
```

API ManagementのAPI subscription key はこちらから
![](/images/graphrag-1_0/2024-12-22-19-00-18.png)

次に、以下を設定します。
```python
file_directory = "ローカルに格納しているナレッジデータ対象のフォルダ"
storage_name = "アップロード先のStorage Container名"
index_name = "ナレッジグラフのインデックス名"
endpoint = "API ManagementのGateway URL"
```

私は以下のように設定しました。
```python
file_directory = "../data"
storage_name = "data"
index_name = "test-01"
endpoint = "https://apim-uugxkaopsbxne.azure-api.net"
```

### Indexの作成とステータスチェック
Index作成のジョブを開始した後、このようにステータスを確認できます。complateになるまで待ちましょう。
![](/images/graphrag-1_0/2024-12-23-22-46-38.png)