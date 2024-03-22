---
title: "AzureOpenAIとLlamaIndexを使い、ナレッジグラフに格納したデータを使ったRAGを行う"
emoji: "🎉"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["AzureOpenAI", "LlamaIndex", "RAG", "ナレッジグラフ", "Neo4j"]
published: false
---

# 構成

以前、こちらの記事でナレッジグラフを使ったRAGをするために、LlamaIndexの概要を紹介しました。
今回は、実際にナレッジグラフを作成し、AzureOpenAIを使ったRAGを検証します。
https://zenn.dev/nomhiro/articles/llama-index-abstract

こちらがやりたいことの概要です。
1. 文章をナレッジグラフに変換し、neo4jに格納します。
2. ユーザメッセージに基づき、ナレッジグラフに格納したデータを検索します。
3. 検索結果をもとに、AzureOpenAIで推論します。
![](/images/rag-using-knowledge-graph/2024-03-20-19-33-29.png)

# 環境構築
- Docker環境があること。
- AzureOpenAIリソースが払い出されており、GPT-35-Turboモデルがデプロイされていること。

## neo4jを起動
neo4jはDockerで起動します。

docker-compose.yamlを作成します。
```yaml
version: '3'
services:
  database:
    image: neo4j
    ports:
      - '7687:7687'
      - '7474:7474'

    environment:
      - NEO4J_AUTH=neo4j/testneo4j
      - NEO4JLABS_PLUGINS=["apoc"]
```

docker-compose upで起動します。
```bash
docker-compose up -d
```

以下のように表示されれば起動完了です。
```bash
[+] Running 1/0
 ✔ Container neo4j-database-1  Created                                                                             0.0s
Attaching to database-1
database-1  | NEO4JLABS_PLUGINS has been renamed to NEO4J_PLUGINS since Neo4j 5.0.0.
database-1  | The old name will still work, but is likely to be deprecated in future releases.
database-1  | Installing Plugin 'apoc' from /var/lib/neo4j/labs/apoc-*-core.jar to /var/lib/neo4j/plugins/apoc.jar
database-1  | Applying default values for plugin apoc to neo4j.conf
database-1  | Skipping dbms.security.procedures.unrestricted for plugin apoc because it is already set.
database-1  | You may need to add apoc.* to the dbms.security.procedures.unrestricted setting in your configuration file.
database-1  | Changed password for user 'neo4j'. IMPORTANT: this change will only take effect if performed before the database is started for the first time.
database-1  | 2024-03-20 07:55:47.942+0000 INFO  Logging config in use: File '/var/lib/neo4j/conf/user-logs.xml'
database-1  | 2024-03-20 07:55:47.974+0000 INFO  Starting...
database-1  | 2024-03-20 07:55:49.697+0000 INFO  This instance is ServerId{9c2b005a} (9c2b005a-a034-4b83-8c81-67c40e84cb18)
database-1  | 2024-03-20 07:55:52.747+0000 INFO  ======== Neo4j 5.17.0 ========
database-1  | 2024-03-20 07:56:03.407+0000 INFO  Bolt enabled on 0.0.0.0:7687.
database-1  | 2024-03-20 07:56:04.839+0000 INFO  HTTP enabled on 0.0.0.0:7474.
database-1  | 2024-03-20 07:56:04.840+0000 INFO  Remote interface available at http://localhost:7474/
database-1  | 2024-03-20 07:56:04.847+0000 INFO  id: C09C0B85EA41EDB35266FFC629E9175B40B5E3C8FECCC593D816C71BECE9D171
database-1  | 2024-03-20 07:56:04.847+0000 INFO  name: system
database-1  | 2024-03-20 07:56:04.848+0000 INFO  creationDate: 2024-03-17T01:51:09.39Z
database-1  | 2024-03-20 07:56:04.848+0000 INFO  Started.
```

ブラウザでhttp://localhost:7474/にアクセスし、neo4jの管理画面が表示されれば問題ありません。
![](/images/rag-using-knowledge-graph/2024-03-20-20-00-22.png)


## ナレッジグラフ化し、neo4jに登録する処理

requirements.txtに以下を記述します。
```txt
langchain
langchain-openai
langchain-community
langchain-text-splitters
openai
neo4j #langchainのneo4jが、neo4jのライブラリを使用する。
bs4 #langChainのWebBaseLoaderが、bs4を使用する。
```

各種ライブラリをインストールします。
```bash
pip install -r requirements.txt
```

### 処理概要

1. ナレッジグラフ化する対象のドキュメントの取得
2. ドキュメントを、LangChainの「CharacterTextSplitter」を使ってチャンク化
3. チャンク化したそれぞれのデータに対し、LangChainの「create_structured_output_chain」を使ってナレッジグラフ化
4. ナレッジグラフ化したデータをneo4jに登録

### 実装

実装においては、こちらのLangChainのサイトを参考にしています。
LangChainのバージョンが新しくなったため、実装修正しています。また、AzureOpenAIを使っているため、AzureOpenAIの設定も行っています。
https://blog.langchain.dev/constructing-knowledge-graphs-from-text-using-openai-functions/

LLMはAzureOpenAIを使いますので、AzureOpenAIの設定と、Neo4jの設定を行います。
```python
import os, logging
from langchain_openai import AzureChatOpenAI
from langchain.graphs import neo4j_graph

azure_openai_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
azure_oepnai_key = os.environ.get('AZURE_OPENAI_KEY')

# AzureOpenAIの設定
llm = AzureChatOpenAI(
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_oepnai_key,
    azure_deployment="gpt-35-turbo"
)

url = "bolt://localhost:7687"
username = "neo4j"
password = "testneo4j"
# Neo4jGraph クラスのインスタンスを作成
graph = neo4j_graph.Neo4jGraph(
    url=url,
    username=username,
    password=password
)
```

次に、ナレッジグラフを表現するためのデータ構造を定義します。
以下の4つのクラスを用意します。
- **Property**：キーと値のペアを表現するためのクラス
- **Node**：グラフのノードを表現するためのクラス
- **Relationship**：グラフのリレーションシップを表現するためのクラス
- **KnowledgeGraph**：ナレッジグラフ全体を表現するためのクラス。ノードのリストとリレーションシップのリストを持ちます。

```python
class Property(BaseModel):
    key: str = Field(..., description="key")
    value: str = Field(..., description="value")

class Node(BaseNode):
    properties: Optional[List[Property]] = Field(
        None, description="List of node properties"
    )

class Relationship(BaseRelationship):
    properties: Optional[List[Property]] = Field(
        None, description="List of relationship properties"
    )

class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(..., description="List of nodes in the Knowledge Graph")
    reles: List[Relationship] = Field(..., description="List of relationships in the Knowledge Graph")
```


次に、ナレッジグラフのノードとリレーションを設定するためのメソッドを定義します。
作成するメソッドは以下の4つです。
- **format_property_key**：プロパティのキーをキャメルケースに変換します。
- **props_to_dict**：グラフデータベースから取得したプロパティのリストをPythonの辞書に変換します。
- **map_to_base_node**：ナレッジグラフのノードをBaseNodeにマッピングします。
- **map_to_base_relationshi**p：ナレッジグラフのリレーションをBaseRelationshipにマッピングします。

```python
def format_property_key(key: str) -> str:
    words = key.split()
    if not words:
        return key
    first_word = words[0].lower()
    capitalized_words = [word.capitalize() for word in words[1:]]
    return "".join([first_word] + capitalized_words)

def props_to_dict(props) -> dict:
    properties = {}
    if not props:
      return properties
    for p in props:
        properties[format_property_key(p.key)] = p.value
    return properties

def map_to_base_node(node: Node) -> BaseNode:
    properties = props_to_dict(node.properties) if node.properties else {}
    properties["name"] = node.id.title()
    return BaseNode(
        id=node.id.title(), type=node.type.capitalize(), properties=properties
    )

def map_to_base_relationship(rel: Relationship) -> BaseRelationship:
    source = map_to_base_node(rel.source)
    target = map_to_base_node(rel.target)
    properties = props_to_dict(rel.properties) if rel.properties else {}
    return BaseRelationship(
        source=source, target=target, type=rel.type, properties=properties
    )
```

次に、ドキュメントのテキスト情報を用いて、OpenAIを使ってナレッジグラフを構築するための関数を定義します。
この段階では、ナレッジグラフのノードとリレーションの種類は指定しません。
ナレッジグラフの作成にはOpenAIを使うので、システムメッセージとユーザメッセージを、LangChainのChatPromptTemplateを使って定義します。
```python
def get_extraction_chain(
    allowed_nodes: Optional[List[str]] = None,
    allowed_rels: Optional[List[str]] = None
    ):
    prompt = ChatPromptTemplate.from_messages(
        [(
          "system",
          f"""# Knowledge Graph Instructions for GPT-4
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts. They're akin to Wikipedia nodes.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it accessible for a vast audience.
## 2. Labeling Nodes
- **Consistency**: Ensure you use basic or elementary types for node labels.
  - For example, when you identify an entity representing a person, always label it as **"person"**. Avoid using more specific terms like "mathematician" or "scientist".
- **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
{'- **Allowed Node Labels:**' + ", ".join(allowed_nodes) if allowed_nodes else ""}
{'- **Allowed Relationship Types**:' + ", ".join(allowed_rels) if allowed_rels else ""}
## 3. Handling Numerical Data and Dates
- Numerical data, like age or other related information, should be incorporated as attributes or properties of the respective nodes.
- **No Separate Nodes for Dates/Numbers**: Do not create separate nodes for dates or numerical values. Always attach them as attributes or properties of nodes.
- **Property Format**: Properties must be in a key-value format.
- **Quotation Marks**: Never use escaped single or double quotes within property values.
- **Naming Convention**: Use camelCase for property keys, e.g., `birthDate`.
## 4. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
## 5. Strict Compliance
Adhere to the rules strictly. Non-compliance will result in termination.
          """),
            ("human", "Use the given format to extract information from the following input: {input}"),
            ("human", "Tip: Make sure to answer in the correct format"),
        ])
    return create_structured_output_chain(KnowledgeGraph, llm, prompt, verbose=False)
```



最後に、ナレッジグラフのデータをNeo4jに登録するための関数を定義します。
※OpenAIによるナレッジグラフの作成でエラーが発生することがあったため、エラーが発生した場合はリトライするようにしています。
```python
def extract_and_store_graph(
    document: Document,
    nodes:Optional[List[str]] = None,
    rels:Optional[List[str]]=None) -> None:
    extract_chain = get_extraction_chain(nodes, rels)
    logging.info(" document.page_content: " + document.page_content)
    try:
        data = extract_chain.invoke(document.page_content)['function']
    except Exception as e:
        logging.error("Error occurred while extracting graph data. Retrying 1 ...")
        try:
            data = extract_chain.invoke(document.page_content)['function']
        except Exception as e:
            logging.error("Error accured. finish.")
            raise e
            
    graph_document = GraphDocument(
      nodes = [map_to_base_node(node) for node in data.nodes],
      relationships = [map_to_base_relationship(rel) for rel in data.reles],
      source = document
    )
    graph.add_graph_documents([graph_document], True)
```


これで必要なメソッドがそろいましたので、実際にナレッジグラフを作成し、neo4jに登録してみます。
以前の私の記事を使います。
LangChainのWebBaseLoaderを使ってWebページの内容を取得し、チャンク化したデータに対して、順次ナレッジグラフを作成しneo4jに登録します。
```python
from langchain.document_loaders import web_base
from langchain_text_splitters import CharacterTextSplitter

raw_documents = web_base.WebBaseLoader(web_path="https://zenn.dev/nomhiro/articles/llama-index-abstract").load()
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=200, chunk_overlap=50)
documents = text_splitter.split_text(raw_documents[0].page_content)
print(documents)

from tqdm import tqdm

# documentsをDocument型に変換します。
document = [Document(page_content=d) for d in documents]
for i, d in tqdm(enumerate(document), total=len(document)):
    extract_and_store_graph(d)
```

実際に動かして、Neo4jのデータを見ると以下のようにナレッジグラフ化されました。
![](/images/rag-using-knowledge-graph/2024-03-23-01-11-45.png)

一部拡大します。この後のRAG処理では、以下のデータに対してクエリを投げてみます。
![](/images/rag-using-knowledge-graph/2024-03-23-01-17-24.png)

## ナレッジグラフに対して、質問してみる

ナレッジグラフに対して、質問を投げてみます。
```python
import os, logging
from langchain_openai import AzureChatOpenAI
from langchain.graphs import neo4j_graph
from langchain.chains.graph_qa.cypher import GraphCypherQAChain

azure_openai_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')
azure_oepnai_key = os.environ.get('AZURE_OPENAI_KEY')

llm = AzureChatOpenAI(
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_oepnai_key,
    azure_deployment="gpt-35-turbo"
)

# Neo4jの接続情報
url = "bolt://localhost:7687"
username = "neo4j"
password = "testneo4j"
# Neo4jGraph クラスのインスタンスを作成
graph = neo4j_graph.Neo4jGraph(
    url=url,
    username=username,
    password=password
)

graph.refresh_schema()

cypher_chain = GraphCypherQAChain.from_llm(
    graph=graph,
    cypher_llm=llm,
    qa_llm=llm,
    validate_cypher=True,
    return_intermediate_steps=True
)

result = cypher_chain("What components does Llamaindex have?")
print(f"Intermediate steps: {result['intermediate_steps']}")
print(f"Final answer: {result['result']}")
```


「What components does Llamaindex have?」という質問に対しては、以下のような結果が返ってきました。期待通りの結果です。
```bash
Intermediate steps: [{'query': "MATCH (f:Framework {name: 'Llamaindex'})-[:HASCOMPONENT]->(c:Component) RETURN c.name"}, {'context': [{'c.name': 'Dataconnector'}, {'c.name': 'Dataindex'}, {'c.name': 'Engine'}]}]
Final answer: The components that Llamaindex has are Dataconnector, Dataindex, and Engine.
```

次は、質問文を日本語にしてみます。「Llamaindexには何のコンポーネントが含まれていますか？」
以下の結果になりました。これも期待通りです。
```bash
Intermediate steps: [{'query': "MATCH (f:Framework {name: 'Llamaindex'})-[:HASCOMPONENT]->(c:Component) RETURN c.name"}, {'context': [{'c.name': 'Dataconnector'}, {'c.name': 'Dataindex'}, {'c.name': 'Engine'}]}]
Final answer: Llamaindexには、Dataconnector、Dataindex、Engineというコンポーネントが含まれています。
```

以下は、**期待通りにならない質問パターン**です。
- LlamaindexをLlamaIndexにする。
「LlamaIndexには何のコンポーネントが含まれていますか？」
以下の結果になりました。期待通りの結果ではありません。
ナレッジグラフ化する際に、Nodeのnameをキャメルケースにしているため、質問文がキャメルケースではないと、正しく検索できません。キャメルケースにしている処理をはずすか、LangChainのGraphCypherQAChainの実装を修正する必要があります。
```bash
Intermediate steps: [{'query': 'MATCH (f:Framework{name:"LlamaIndex"})-[:HASCOMPONENT]->(c:Component) RETURN c.name'}, {'context': []}]
Final answer: その答えは私にはわかりません。
```

# 見えてきた課題

データを見ると、以下の問題点がありそうです。
- チャンク化したデータをまたいで、リレーションが張られていない。
  - これは、チャンク化するとドキュメント全体の文脈がなくなるので、関連性が途切れてしまうことが原因と考えられます。チャンク数の工夫や、オーバーラップ数を増やす調整が必要かもしれません。
- 作成されるノードのid, nameが適切でない。
  - 文章内でNodeにしてほしい単語がNodeになっていないことが多々あります。日本語だから精度が微妙なのでしょうか。。
- 一部、英語に変換されたNodeと、日本語のままのNodeがあります。
  - ここはナレッジグラフ化するプロンプトの調整が必要かもしれません。
- Neo4jに対するクエリは、単語一致なので、文字の揺れがあると対応できない。
  - これは、ベクトル値をNodeに入れて、ベクトル検索することで解決できそうです。


# まとめ
ずっと気になっていた、ナレッジグラフを使ったRAGを実装してみました。
実際に検証してみると、ナレッジグラフ化する際の問題点が多数ありました。
今後は、Nodeにベクトル値を格納し、ベクトル検索して検索精度を上げられるか試してみようと思います。
