---
title: ""
emoji: "📝"
type: "【OmniRAG】Azure Cosmos DB のナレッジグラフによる GraphRAG を試す" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# Azure Cosmos DB のナレッジグラフ
https://learn.microsoft.com/ja-jp/azure/cosmos-db/gen-ai/cosmos-ai-graph

従来のRAGはベクトル検索。分類によるフィルターなどは可能とはいえ、
社内業務を、階層に分けて構造的にRAGできる仕組みではない。

ナレッジグラフ・・・グラフ構造にデータを保持するため、要素同士の関係性を定義できる。ナレッジグラフとベクトル検索を組み合わせてRAGする。


ナレッジグラフが有効なユースケース
- 要素同士の関係性を考慮したうえで回答してほしい
  - 例）組織内の人間関係
- 要素の階層構造を考慮したうえで回答してほしい
  - 例）組織構造、
- つながりのある情報を考慮して回答してほしい
  - 例）部品サプライチェーンの調達～製品納入までの手順

ベクトル検索が向くケース
- 類似性のあるナレッジを回答する。
  - 画像やドキュメント取得で役立つ。

# OminiRAG
OmniRAGとは、データベースクエリ、ベクトル検索、ナレッジグラフ走査の中から、最も適切な方法を動的に選択することで、ユーザクエリに対して正確性高く回答するための、データ取得部分に汎用性の高いアプローチ。各検索(データ取得)方法の長所を活かしたつくりといえる。
動的選択で重要なのは、ユーザの質問から推察される「**ユーザの意図**」が大切。
例えば、類似ドキュメントを知りたいならベクトル検索、紐づく情報のことを知りたいならナレッジグラフという具合

RAGプレオセス内でオーケストレーションを使うことで、複数のソースを試用してAIのためのコンテキストを収集できる。
例：最初にGraph走査してから、Graphで取得したエンティティの詳細情報をデータベースレコードからクエリしてもよい。結果が何も見つからなかったならベクトル検索で類似性の高いデータを取得する。
Microsoft の公式ページでは、以下のような例があげられている。
| ユーザの質問 | 戦略 |
| --- | --- |
| Python Flask ライブラリとは? | DB RAG |
| どんな依存関係があるか? | Graph RAG |
| 非同期処理を使用する代替案は？ | Vector RAG |
| 作成者は? | DB RAG |
| 彼女が書いたその他のライブラリは? | Graph RAG |
| すべてのライブラリとその依存関係のグラフを表示する | Graph RAG |

# GraphAIGraphの前提
https://github.com/nomhiro/CosmosAIGraph
- Microsoft, Azure, CosmosDBの製品ではない
- CosmosDB Mongo vCore、またはNoSQL PaaSサービスとして稼働
- ベクトル検索可能
- RDFテクノロジー - トリプル、OWLオントロジー（スキーマ）、SPARQLクエリ
- インメモリグラフ - LinkedInにインスパイアされ、より高速なパフォーマンスと低コストを実現。
- BicepでAzure Container Apps (ACA)にデプロイ。 またはAKS。 
- DBはCosmos DB1つだけで、シンプルなアーキテクチャ
- Omni RAGの概念を導入し、実装

::: details Resource Description Framework (RDF)
- W3C標準のひとつ。  20年前の成熟したもの。
- 一般的にナレッジグラフに使用される
- ラベル付きプロパティグラフ(LPG)に代わるデザイン
:::

::: details Web Ontology Language (OWL)
- グラフのClassとObjectPropertiesを定義するXML構文
- これらをEntityとRelationship、GraphSchemaととらえる
:::

::: details Triples
- ( 主語、述語、目的語 ) のタプル
  - 例： ( Cosmos DB → has_api → vCore ) 
- RDFグラフは、これらの単純なトリプルとオントロジーから構成される。
- 概念的に単純
:::

::: details SPARQL1.1
問い合わせ言語。 SQLに似ている。 Gremlin & Cypherよりシンプル。
:::

::: details Apache Jena 
- オープンソースの RDF データベース実装。
:::

## Graphデザインと開発ステップ
1. Cosmos DBアカウントの設計とロード
   - 典型的なNoSQLデザインパターン、JSONドキュメントを使用
   - 特別な 「トリプル 」ドキュメントは不要
2. グラフスキーマの定義
   - XML構文です。 クラス、データ型付き属性、リレーションシップの定義
3. Cosmos DBからインメモリRDFデータベースをロードする。
   - 適切なCosmos DBドキュメントの必要な属性のみを読み込む。 サブセット。
   - AppGraphBuilderクラスから呼び出されるGraphTriplesBuilderクラスを実装する。
   - 観測されたデータメタデータ/構造に基づいてコード生成を使用する可能性がある。
   - グラフは厳密にはインメモリ実装であり、ディスク上には存在しない。
   - あるいは、開発環境では、RDFファイル（つまり、*.nt）からグラフをロードする。
4. インメモリRDFデータベースにSPARQLでクエリーする。
   - インメモリなので非常に速い。
   - ベクトル化が不要なため、低コストである。
   - SPARQLはオプションでGenAI & Azure OpenAIで生成できる。 これは素晴らしい学習ツールだ

## 生成AIユースケース
1. ユーザの自然言語から「RAG戦略」を推測する 
   - OpenAIとプロンプトで 「LUISのような 」発話、エンティティ、インテントを実装する
   - StrategyBuilder#determineクラスを参照。
2. ユーザー自然言語からSPARQLクエリを生成する
   - システムプロンプトとしてOWLオントロジーを使用する
   - AIService#generate_sparql_from_user_prompt を参照。
3. 入力データをCosmos DBドキュメントに取り込むためのコードを生成する（オプション
   - CSVヘッダー、JSON構造から入力スキーマを推測
   - 定義されたOWLオントロジーを対象とする

## CosmosAIGraphのアプリロジック
1. ユーザーの意図から意図とRAG戦略を決定する
2. エンティティを識別する
3. クエリ生成
   - グラフRAGの場合はSPARQLクエリを生成する
   - DB RAGの場合はCosmos DBクエリを生成する
   - ベクトルRAGの場合はユーザー入力をベクトル化する
4. DBクエリを実行してドキュメントリストを取得する
5. Cosmos DBからリストごとにドキュメントを取得する
6. ドキュメントRAGデータでプロンプトを作成する
7. プロンプト内の入力とRAGデータでLLMを呼び出す
8. LLMの応答を解析し、Web UIに表示する

## CosmosAIGraphアプリケーションのアーキテクチャ
![](/images/cosmos-ai-graph-rag/2025-01-26-01-40-30.png)

# トライ
※CosmosDB for NoSQLを使う

順序
1. Azure CosmosDB と Azure OpenAI のプロビジョニング
2. 開発環境のセットアップ
3. CosmosDBのドキュメント構成とモデリング、NoSQLの設定
4. アプリ実行
5. Azure Container App へのデプロイ