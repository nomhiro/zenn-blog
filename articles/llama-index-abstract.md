---
title: "RAGフレームワーク LlamaIndex の概要を整理してみる"
emoji: "🦙"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["LLM", "OpenAI", "RAG", "LlamaIndex", "GPT"]
published: false
---

# はじめに
LLMは、トレーニングしたデータを使い推論するため、学習した時点の情報でしか推論できません。これを補うのがRAG（検索拡張生成 Retrieval-Augmented Generation）手法です。LLMへのプロンプトに、検索して取得した情報を追加することで、最新かつユーザが欲しい情報をもとに推論されます。
システム構成は、AzureでRAGを構築する際によくあるこのようなパターンです。
![](/images/llama-index-abstract/2024-02-26-23-25-21.png)
https://learn.microsoft.com/ja-jp/azure/search/retrieval-augmented-generation-overview

私が今まで構築してきたRAGシステムも、ドキュメントとユーザクエリのベクトル類似度が高いものを検索し、LLMで推論する方法です。この方法で、多量のドキュメントの中から類似度の高い情報から推論することができます。
:::message
**ただ、実際の業務では類似度による検索だけではなく、ドキュメント間の関連性が重要な場面が多いです。検索したドキュメントに関連する情報をどのように取得すればいいのか、その関連性をどのように表現し検索するかが課題でした。**
:::

この課題を解決する方法の一つとして、GraphDBを使ってドキュメントの関連性を表現することができると思います。ドキュメントを点とみなし、その点を結ぶ線が関連性を表せるようにデータを構築します。
GraphDBを使ったRAGは以下ののようなイメージです。
1. まずユーザクエリに対して、類似度の高いドキュメントを検索します。
2. そのドキュメントに関連するドキュメントも取得できます。
3. 取得できた関連ドキュメントも一緒に、LLMで推論します。

このようなことを考えて調べていたら、こちらのMicorosftResearchブログを見つけました。
https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/

この記事では、上記ブログで紹介されているLlamaIndexの概要を整理してみます。

# LlamaIndexとは
こちらがLlamaIndexのドキュメントです。
https://docs.llamaindex.ai/

まず概要をまとめます。
- LlamaはRAGシステムを構築するためのフレームワーク
- PythonとTypescriptで利用可能
- 外部データをAPIやSQLを使って取り込む**データコネクタ**が用意されている
- データを構造化して保持する**データインデックス**が用意されている
※様々な構造化パターンがあるので後述します。
- 構造化されたデータに自然言語でアクセスするための**エンジン**
※検索のためのクエリエンジンや、マルチメッセージのためのチャットエンジン

:::message
**ただ単にドキュメントを検索インデックスにするだけではなく、ツリーやグラフDBなどのような形式で構造化してデータを保持しインデックス化することが特徴のようです。**
:::

## RAGの流れ
LlamaIndexで用意されているツール群を把握するためには、それらのツール群がRAGのどのフェーズで使われるかを理解することが重要です。
https://docs.llamaindex.ai/en/stable/getting_started/concepts.html#retrieval-augmented-generation-rag
RAGのフェーズは以下のようになります。
![](/images/llama-index-abstract/2024-02-26-23-43-16.png)
1. **Loading** : [LlamaHub](https://llamahub.ai/)が用意されていて、ドキュメントの読み込み、ほかデータベースからのデータ取り込みが可能。
2. **Indexing** : ドキュメントからメタデータを取得してベクトル化し、データ構造を作成
3. **Storing** :  Indexingして構造化したデータを保存する
4. **Quering** : サブクエリ、マルチステップ クエリ、ハイブリッドクエリなどの種類があり、LLM と LlamaIndex データ構造を利用してクエリを実行できる。
5. **Evaluating** : クエリに対する回答がどれだけ正確か評価する

## 1. Loadingフェーズ

#### LlamaIndexに格納するデータ(オブジェクト)の種類
https://docs.llamaindex.ai/en/stable/module_guides/loading/documents_and_nodes/root.html
LlamaIndexに格納するオブジェクトには、「Documentオブジェクト」と「Nodeオブジェクト」の2種類があります。
- Documentオブジェクト
  - PDF、API出力、データベースから取得したデータなどから取得したデータ構造を格納するための汎用コンテナ。マルチモーダルに対応できるようにベータ版機能が公開されてます。（Excelのように、テキスト、グラフ、表、図などが混じっていてもデータ化できると嬉しい。）
  - ドキュメントにはテキスト自体とメタデータが格納。
    - metadata - テキストに追加する注釈辞書（タグ的な考え方）
    - relationships - 他のドキュメントやノードとの関係を含む辞書
- ノードオブジェクト
  - ドキュメントのチャンク単位がノード
  - ドキュメントと同様にmetadataとrelationshipの情報が含まれる。
  - ドキュメントから派生したすべてのノードは、ドキュメントのメタデータ（file_nameなど）を継承。

#### データコネクタ
https://docs.llamaindex.ai/en/stable/module_guides/loading/connector/root.html

データコネクトは[LlamaHub](https://llamahub.ai/)で提供されている機能を使います。
いろいろありすぎますね。
![](https://storage.googleapis.com/zenn-user-upload/692cab47ef5c-20240218.png)
図やグラフ、表を含むExcelやPowerpointにどこまで対応しているか、個人的には気になります。追々検証。。。

## 2. Indexingフェーズ

#### 各Indexの仕組み
- サマリーインデックス（旧リストインデックス）
  - ノードをシーケンシャルチェーンとして格納
  ![](/images/llama-index-abstract/2024-02-26-23-55-51.png)
- ベクターストアインデックス
  - 各ノードとそのベクトル値を格納
  ![](/images/llama-index-abstract/2024-02-26-23-56-07.png)
- ツリーインデックス
  - ノードを階層ツリーにして格納
  - クエリ結果には、ルートノードからリーフノードへのノードが含まれる。```child_branch_factor```に設定された数に応じて、何個の子ノードを取得するかを設定する。
  ![](/images/llama-index-abstract/2024-02-26-23-56-25.png)
- キーワードテーブルインデックス
  - 各ノードからキーワードを抽出し、 各キーワードを、そのキーワードの対応するノードに設定する。
  - クエリ時は、クエリからキーワードを抽出し、そのキーワードにマッチするノードを取得する。
  ![](/images/llama-index-abstract/2024-02-26-23-57-04.png)

- Knowledge Graph Index
  - KnowledgeGraphによるGraphDBの組み立て方を知りたかったのですが、、、、ドキュメントには解説がなかったため、のちの実検証記事で紹介します...！
https://docs.llamaindex.ai/en/stable/examples/index_structs/knowledge_graph/KnowledgeGraphDemo.html

## 4. Queringフェーズ

### Retriever
https://docs.llamaindex.ai/en/stable/module_guides/querying/retriever/root.html
ユーザのクエリに対して最も関連性の高いコンテキストを取得する方法を定義します。

基本的には、RetrieverはIndexに定義されるものです。（個別定義もできるようです。）

RetrieverにはIndexに応じて複数のモードがあります。

- VectorIndex
- SummaryIndex
- TreeIndex
- KeywordTableIndex
- KnowledgeGraphIndex
- DocumentSummaryIndex

https://docs.llamaindex.ai/en/stable/module_guides/querying/retriever/retriever_modes.html

### Router
https://docs.llamaindex.ai/en/stable/module_guides/querying/router/root.html

**Routerがナレッジベースから関連するコンテキストを取得するためにどのRetrieverを利用するかを決めます。**（クエリを実行する 1 つ以上のRetrieverを選択する）
このような処理の流れになるようです。
- 多数のデータソースから最適なデータソースを選択する
- 要約やセマンティック検索を実行するか決める
- 一度に多数の選択肢を試し、その結果を組み合わせるかどうかを決める。（マルチルーティング機能）

### Node Postprocessor
https://docs.llamaindex.ai/en/stable/module_guides/querying/node_postprocessors/root.html

RouterやRetrieverで選択されたIndexで取得したノード群を取り込み、変換、フィルタリング、再ランク付けのロジックを実行する役割です。

### Response Sysnthesizers
https://docs.llamaindex.ai/en/stable/module_guides/querying/response_synthesizers/root.html

**ユーザクエリとデータストアから取得しNodePostprocesserで変換されたテキストチャンクをのセットを使用し、LLMでユーザクエリに対する応答を生成する役割です。**

応答を生成する方法もいくつかの種類があります。種類と概要をまとめます。
- refine
  - 取得した各テキストチャンクを順番に調べて回答を作成し、絞り込む。取得したチャンクごとに個別のLLM呼び出しが行われる。
- compact
  - refineとほぼ同じだが、事前にチャンクを圧縮(連結)するためLLM呼び出しを少なくできる。LLMの入力トークンに収まる分だけ、テキストチャンクを連結する。
- tree_summarize
  - まずLLMの入力トークンに収まる分だけ、テキストチャンクを連結し、その数だけ推論する。
  - 次に推論結果を連結し、さらにクエリを実行する。回答が1つになるまでこの処理を続ける。
  - 要約に適している。
- simple_summarize
  - すべてのテキストチャンクを切る捨てて、1つのLLMプロンプトに収める。
  - 手っ取り早く要約したい場合に向いているが、切り捨てにより詳細情報が抜け落ちる可能性がある。
- no_text
  - Retrieverのみを実行して、LLMに送信されるノードを取得する。
- accumulate
  - テキストチャンクのセットに対し、ここにクエリを実行し、その結果の配列を変える。
  - 各テキストチャンクに対して同じクエリを個別に実行したい場合に使う
- compact_accumulate
  - accumulateとほぼ同じだが、事前にテキストを圧縮(連結)するためLLM呼び出しを少なくできる。LLMの入力トークンに収まる分だけ、テキストチャンクを連結する。



# まとめ
まずはLlamaIndexのRAGフレームワークに使われる各モジュールの概要を整理しました。
今後、実際に動作検証していき、とくにKnowledgeGraphIndexについては、詳しく仕組みを調べていきたいと思います。

# 参考
実際に、Webサイトの情報をKnowledgeGraphにして、Neo4jに保管し、RAGをすることを試しました。
https://zenn.dev/nomhiro/articles/rag-using-knowledge-graph