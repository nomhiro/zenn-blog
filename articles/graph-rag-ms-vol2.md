---
title: "GraphRAG 第二弾 ~ どのようにGraphデータが登録される？ ~ "
emoji: "🦔"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# はじめに
前回はこちらの記事でGraphRAGをAzureにデプロイし、動作確認しました。
https://zenn.dev/nomhiro/articles/graph_rag_ms

今回は、これらを解説、確認します。
- **CosmosDBの用途**
- **用意されているAPIの解説**
- **GraphRAGで登録したGraphデータがどのように登録されているのか**

# 基本的な概念
以下２つのフェーズがあります。
- Graphデータを生成するための「Indexing」処理
- Graphデータを使い検索し、質問に回答する「Query」処理

## Index
オープンソースライブラリであるDataShaperの上に構築されている。
DataShaperは、データの整形や変換を行うためのライブラリ。ワークフローの中に、データの前処理、後処理、変換、結合などのステップ（DataShaperではVerbと呼ばれる）を定義できます。


- 入力コーパスを一連のTextUnitに分割し、これらをプロセスの残りの部分で分析可能な単位として扱い、出力に細かい参照を提供します。 
- LLMを使用して、TextUnitからすべてのエンティティ、関係、および主要な主張を抽出します。 
- Leiden技法を使用してグラフの階層的クラスタリングを実行します。これを視覚的に確認するには、上記の図1を参照してください。各円はエンティティ（例：人、場所、組織）を表し、サイズはエンティティの度合いを、色はそのコミュニティを表します。 
- データセットの全体的な理解を助けるために、各コミュニティとその構成要素の要約をボトムアップで生成します。

## Query
- **グローバル検索**
  - コミュニティの要約を活用して、コーパス全体に関する包括的な質問に対する推論を行います。 
  - https://arxiv.org/pdf/1810.08473
- **ローカル検索**
  - 特定のエンティティに関する推論を行うために、その隣接エンティティや関連する概念にファンアウトします。
  - https://arxiv.org/pdf/1810.08473

## Prompt Tuning
- GraphRAGをデータと共にそのまま使用すると、最良の結果が得られない可能性があります。
ドキュメントのプロンプトチューニングガイドに従ってプロンプトを微調整することを強くお勧めします。

# CosmosDBの用途

以下のコンテナが作成されます。
- container-store
- entities
- jobs

### contaienr-store

作成したGraphRAGのインデックス名が格納されます。

:::details container-storeコンテナ内アイテムの例
```json
{
    "id": "c7c20c61a8e8fd13a71d43af3ca57f70",
    "human_readable_name": "test_wiki_jp",
    "type": "index",
    "_rid": "Avd4AL3LEVoHAAAAAAAAAA==",
    "_self": "dbs/Avd4AA==/colls/Avd4AL3LEVo=/docs/Avd4AL3LEVoHAAAAAAAAAA==/",
    "_etag": "\"0100861e-0000-2300-0000-66932a370000\"",
    "_attachments": "attachments/",
    "_ts": 1720920631
}
```

### entities

Index作成後、entitiesコンテナのアイテムはゼロ件でした。
てっきり、データから抽出した単語群が登録されているかと思いましたが、違いました。

### jobs

各Graphインデックスを作成するためのジョブ進捗状況が格納されます。
インデックス作成のステータスはAPI（GET /index/status/{index_name}）からも取得できますが、そのAPIはこのコンテナのデータを取得しています。

:::details jobsコンテナ内アイテムの例
終わったジョブ名が、completed_workflowsに格納されていきます。
```json
{
    "id": "c7c20c61a8e8fd13a71d43af3ca57f70",
    "index_name": "c7c20c61a8e8fd13a71d43af3ca57f70",
    "storage_name": "c7c20c61a8e8fd13a71d43af3ca57f70",
    "all_workflows": [
        "create_base_documents",
        "create_final_documents",
        "create_base_text_units",
        "join_text_units_to_entity_ids",
        "join_text_units_to_relationship_ids",
        "join_text_units_to_covariate_ids",
        "create_final_text_units",
        "create_base_extracted_entities",
        "create_summarized_entities",
        "create_base_entity_graph",
        "create_final_entities",
        "create_final_relationships",
        "create_final_nodes",
        "create_final_communities",
        "create_final_community_reports",
        "create_final_covariates"
    ],
    "completed_workflows": [
        "create_base_text_units",
        "create_base_extracted_entities",
        "create_final_covariates",
        "create_summarized_entities",
        "join_text_units_to_covariate_ids",
        "create_base_entity_graph",
        "create_final_entities",
        "create_final_nodes",
        "create_final_communities",
        "join_text_units_to_entity_ids",
        "create_final_relationships",
        "join_text_units_to_relationship_ids",
        "create_final_community_reports",
        "create_final_text_units",
        "create_base_documents",
        "create_final_documents"
    ],
    "failed_workflows": [],
    "status": "complete",
    "percent_complete": 100,
    "progress": "16 out of 16 workflows completed successfully.",
    "_rid": "Avd4AMzL2icEAAAAAAAAAA==",
    "_self": "dbs/Avd4AA==/colls/Avd4AMzL2ic=/docs/Avd4AMzL2icEAAAAAAAAAA==/",
    "_etag": "\"4000d29e-0000-2300-0000-66933b890000\"",
    "_attachments": "attachments/",
    "_ts": 1720925065
}
```
:::

# ナレッジグラフの内容

graphmlファイルの形式で、Graphデータが生成されている。
APIがあるのでファイルに出力し確認可能。

ビジュアル的に確認するには、Gephiというグラフデータ描画OSSアプリを使う。
https://gephi.org/

インストール
![](/images/graph-rag-ms-vol2/2024-07-13-11-41-30.png)

![](/images/graph-rag-ms-vol2/2024-07-13-11-43-04.png)

インストーラをDLし実行し、表示に従ってインストールしましょう

「Associaate .graphml files」をチェックに入れておきます。
![](/images/graph-rag-ms-vol2/2024-07-13-11-59-42.png)

インストール完了後、Gephiを起動します。

GraphRAGで登録したGraphデータを確認するために、GraphMLファイルを読み込みます。
![](/images/graph-rag-ms-vol2/2024-07-13-12-02-09.png)

![](/images/graph-rag-ms-vol2/2024-07-13-12-02-21.png)

![](/images/graph-rag-ms-vol2/2024-07-13-12-02-32.png)

Graph描画はされたので、中身を少し見ていきます。
![](/images/graph-rag-ms-vol2/2024-07-13-12-03-08.png)


# AKS

IndexingはAKSのJobとして実行されます。
こちらはIndexing実行時のジョブです。
![](/images/graph-rag-ms-vol2/2024-08-02-20-07-59.png)

このジョブのPodのログを確認すると、Indexingの進捗状況がログにも出力されています。
![](/images/graph-rag-ms-vol2/2024-08-02-20-10-15.png)

Indexing処理が終わったら、JobのPodは終了します。


# APIの解説
## Existing APIs

| HTTP Method | Endpoint         | 概要          | backendソースのファイル名   |
|-------------|------------------|---------------|---------------------------|
| GET         | /data | Graphインデックスを作成するtxtファイルが格納されるストレージコンテナの一覧を取得する | data.py |
| POST        | /data | Graphインデックスを作成するtxtファイルをストレージコンテナにアップロードする | data.py |
| DELETE      | /data/{storage_name} | 指定したストレージのコンテナを削除する | data.py |
| GET         | /index | Graphインデックスの一覧を取得する | index.py |
| POST        | /index
| DELETE      | /index/{index_name}
| GET         | /index/status/{index_name}
| POST        | /query/global
| POST        | /query/local
| GET         | /index/config/prompts
| GET         | /source/report/{index_name}/{report_id}
| GET         | /source/text/{index_name}/{text_unit_id}
| GET         | /source/entity/{index_name}/{entity_id}
| GET         | /source/claim/{index_name}/{claim_id}
| GET         | /source/relationship/{index_name}/{relationship_id}
| GET         | /graph/graphml/{index_name}
| GET         | /graph/stats/{index_name}

### POST /indexの解説
インデックス作成パイプラインを作成します。
setup_indexing_pipelineと_start_indexing_pipelineの2つの主要な関数が含まれています。



#### setup_indexing_pipeline関数
- 概要：インデックス作成プロセスを初期化する。
- Input：
  - ストレージ名
  - インデックス名
  - （オプション）3つのプロンプトファイル（エンティティ抽出、コミュニティレポート、説明の要約）
- 処理順
  1. **Inputの検証**
     - インデックス名とストレージ名がAzure Blob Storageの命名規則に従っていることを確認。
  2. **データコンテナの存在確認**
     - 指定されたストレージ名のコンテナが存在するかどうかを確認。
  3. **プロンプトファイルの内容読み込み**
     - 提供されたプロンプトファイル（存在する場合）から内容を読み込み。
  4. **インデックスジョブの状態確認**
     - 既に同名のインデックスジョブが存在し、実行中またはスケジュールされている場合はエラーを返す。
     ※CosmosDBの「jobs」コンテナのアイテムからジョブ情報取得
     - 失敗状態のジョブがある場合は、失敗したジョブを削除して新しいジョブをスケジュールする。
  5. **CosmosDBの更新**
     - インデックスに関する情報をCosmosDBに保存または更新。
  6. **AKSジョブのスケジュール**
     - Kubernetes上でインデックス作成ジョブを登録。「_generate_aks_job_manifest」で現在のPodの情報を使用してジョブマニフェストを生成し、ジョブを作成する。ジョブで実行されるPythonファイルは「run-indexing-job.py」
     Kubernetes上のジョブについては後述。


### GraphRAGのインデックス作成ジョブの詳細
https://microsoft.github.io/graphrag/posts/index/1-default_dataflow/

run-indexing-job.py（/graphrag-accelerator/backend/src/api/index.py）が実行されます。

- Input
  - インデックス名
- 処理順 ※index.pyの「_start_indexing_pipeline」関数
  - NLTK（Natural Language Toolkit）の依存関係をダウンロードするためにbootstrapする。※テキスト処理や自然言語処理タスクに必要なライブラリやデータセットが準備される。
  - プロンプトが提供されている場合、それらはファイルに書き込まれ、設定データに追加される。

- デフォルトのパイプライン設定を生成し、カスタム設定で上書き　※create_graphrag_config.pyの「create_graphrag_config」関数
  - parallelization にLLMモデルのURL、APIキーを設定
  - embeddings にLLMモデルのURL、APIキーを設定
  - Node2Vecアルゴリズムの設定
  - input ファイルを読み込むための設定。（ファイルエンコーディングや、格納先のStorageAccountのBlobURLなど）
  - Node2Vecを実行するための設定。（ノードの埋め込みを生成するための設定）
  ※Node2Vecとは、グラフデータをベクトル表現に変換する手法の一つ。グラフデータをベクトル表現に変換する。詳細はこちら（https://zenn.dev/kami/articles/e0b62ac3bb05a1）
  - キャッシュストレージの設定。（キャッシュストレージのBlobURL）　用途は？
  - ストレージの設定。（BlobURL）　※キャッシュストレージとの違いは？用途は？
  - データをチャンク化するための設定。
  - GraphML形式でスナップショットを保存するための設定。
  - UMAP（Uniform Manifold Approximation and Projection）モデルの設定。
  ※UMAP（Uniform Manifold Approximation and Projection）は、高次元データの次元削減技術の一つ。t-SNE（t-Distributed Stochastic Neighbor Embedding）と同様に、UMAPは高次元空間におけるデータポイント間の局所的な距離関係を保持しながら、それらを低次元空間（通常は2次元または3次元）にマッピングします。このプロセスにより、データの可視化やクラスタリングが簡単になります。
  - Entity 抽出のための設定。（LLM、プロンプトの設定など）
  - Claim 抽出のための設定。（LLM、プロンプトの設定など）
  - Community Report のための設定。（LLM、プロンプトの設定など）
  - Summarize Description のための設定。（LLM、プロンプトの設定など）
- パイプラインジョブの詳細をリセットし、コールバックマネージャーにパイプラインジョブのコールバックを登録します。

最後に、run_pipeline_with_config関数を使用してパイプラインを非同期に実行します。各ワークフローの結果を処理し、エラーがある場合はそれを記録します。全てのワークフローが完了した後、ジョブの状態を更新し、成功または失敗に応じて適切なアクションを取ります。例外が発生した場合は、ジョブの状態を失敗に設定し、エラーメッセージをログに記録した後、HTTPExceptionを発生させます。


# カスタムプロンプトの設定
GraphRAGは、エンティティとその間の関係を識別する能力に基づいて、データから知識グラフを構築する。プライベートデータに対してGraphRAGが構築する知識グラフの品質を向上させるために、"自動テンプレート生成 "と呼ばれる機能を提供する。この機能は、ユーザから提供されたデータサンプルを受け取り、そのデータの特徴に基づいてカスタム化されたプロンプトを生成する。これらのカスタムプロンプトには、エンティティや関係性の数ショット例が含まれており、これを用いてグラフグラグインデックスを構築することができる。