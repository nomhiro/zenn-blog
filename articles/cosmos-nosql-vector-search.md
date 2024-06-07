---
title: "Azure CosmosDB for NoSQLでベクトル検索を使おう！"
emoji: "🌏"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "CosmosDB", "NoSQL", "ベクトル検索", "Vector"]
published: false
---

# はじめに

Microsoft Build 2024 で、Azure CosmosDB for NoSQLにベクトル検索が追加されました。
https://devblogs.microsoft.com/cosmosdb/build2024-cosmos-roundup/
それまではCosmosDBでは for MongoDBでしかベクトル検索ができませんでした。

これにより、もともとCosmosDBに格納していたデータを活かせる幅が広がると思います。

## CosmosDBの利用シーンを考えてみます。

AzureOpenAIサービスを活用したアプリケーションにおいて、ベクトル検索が導入されたCosmosDB for NoSQLの用途をいくつか考えてみます。

#### １．AISearchの代わりにCosmosDBのベクトル検索使っちゃおう
今までであれば、RAGのためのデータは、検索のためにAISearchにIndex化して格納することが一般的だったと思います。
AISearchのハイブリッド検索やセマンティック検索を利用する必要がない場合であれば、CosmosDB for NoSQLのベクトル検索だけで、RAGのためのデータ構築ができてしまいます。
![](/images/cosmos-nosql-vector-search/2024-06-08-02-23-23.png)

**メリットとしては、以下が挙げられます。**
- AISearchは基本料金が高いので、CosmosDBを使うことでコスト削減になる。
- CosmosDBはデータベースなので、RAGの仕組みだけではなく他システムからのデータ活用もできる。

**一方で、デメリットもあります。**
- AISearchのIndexerのような機能はないので、自身の実装でベクトル化＆CosmosDBへの格納を行う必要があります。
- AISearchでは、サポートされているドキュメント種類（PDF、Word、Excelなど）は自動でIndexerやSkillsetを使ってIndex化されますが、CosmosDBのベクトル検索は自分でIndex化する必要があります。

#### ２．過去に似た問い合わせはこれだよ
RAGでチャットアプリを構築している場合は、チャットログをDBやStorageに格納しているはずです。
ベクトル検索ができるようになったことで、CosmosDBに過去のチャットログを格納し、新たな問い合わせに対して過去の似たチャットをベクトル検索で取得できます。
![](/images/cosmos-nosql-vector-search/2024-06-08-02-23-57.png)

#### 3.チャットログの分析
２．のようにCosmosDBに蓄積されたチャットログの分析にも活用できそうです。
例）似ている問い合わせがどのくらいの頻度で行われているのかなど。


# CosmosDB for NoSQLのベクトル検索の使い方

## 概要

公式ドキュメントはこちらです。
https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/vector-search

ベクトルインデックスの種類が３つあります。
1. **flat**
   - 他のインデックス プロパティと同じインデックスにベクトルを格納
   - ベクトル次元数は最大505
   - メリット：quantizedFlatのようなベクトル値が圧縮は行われないため、100%の精度でベクトル値を検索できる。
   - デメリット：検索時には、全ベクトル値を全検索するため、ベクトル数が多いと検索時間がかかる可能性あり。
2. **quantizedFlat**
   - インデックスに格納する前にベクトル値を圧縮する。
   - ベクトル次元数は最大4096
   - メリット：flatよりも検索時間が短く、RUの消費も少ない。
   - デメリット：圧縮するので精度がflatよりも低くなる可能性がある。
3. **diskANN**
   - 高速で効率的な近似ニアレストネイバー（ANN）検索を行うための特別なインデックス。
   Microsoft Researchによって開発されたDiskANNアルゴリズムを使っているそうです。※中身まで追ってないです。。。
   - メリット：検索時間が短く、RUの消費も少ない。
   - デメリット：まだプレビュー段階のモードなので、精度が低い可能性がある。使うには申請も必要。

diskANNについては、プレビュー段階の機能なので導入には精度検証が必要だと思います。

::: message
**OpenAIのEmbeddingモデルでベクトル化する場合、ベクトル空間は1536次元以上です。
ですので、2024年6月の時点で、業務アプリへ組み込みを行う場合はquantizedFlatを使っておくのが無難だと思います。**
:::

## ベクトル検索のための設定

公式ページに設定内容が記載されています。
https://learn.microsoft.com/ja-jp/azure/cosmos-db/nosql/vector-search#vector-indexing-policies

必要な設定は、２つです。
- ベクトルポリシー
- ベクトルインデックスポリシー

※CosmosDBのアカウント作成、データベース作成は従来通りなので省略します。

アカウント作成後にVectorSearchforNoSQLの機能を有効化します。
![](/images/cosmos-nosql-vector-search/2024-06-08-02-35-27.png)

コンテナ作成時にベクトルポリシーとインデックスポリシーのJson設定を行います。
![](/images/cosmos-nosql-vector-search/2024-06-08-02-54-38.png)

ベクトルポリシーのJson
```json
{
    "vectorEmbeddings": [
        {
            "path": "/content_vector",
            "dataType": "float32",
            "dimensions": 1536,
            "distanceFunction": "cosine"
        }
    ]
}
```

ベクトルインデックスポリシーのJson
```json
{
    "indexingMode": "consistent",
    "automatic": true,
    "includedPaths": [
        {
            "path": "/*"
        }
    ],
    "excludedPaths": [
        {
            "path": "/\"_etag\"/?"
        }
    ],
    "vectorIndexes": [
        {
            "path": "/content_vector",
            "type": "quantizedFlat"
        }
    ]
}
```


## 実装します

### CosmosDBへのデータ登録

まずは、データを入れて検索してみましょう。

今回サンプルとして利用するデータは総務省から提供されている統計データです。2024年1-3月のGDPのデータです。
https://www.esri.cao.go.jp/jp/sna/menu.html
以下のようなPDFファイルをテキスト化したデータです。テキスト化した文字列をベクトル化してCosmosDBに格納します。
![](/images/cosmos-nosql-vector-search/2024-06-08-02-59-35.png)

データ登録では、実際にはLangChainやOpenAI, Azure Document Intelligenceなどのサービスを利用して、PDFファイルをテキスト化する必要があります。
ここでは、テキスト化されたあとのPythonのコード例を以下に示します。

まず、OpenAIのEmbeddingモデルでベクトル化します。

```python
import os
from openai import AzureOpenAI

self.client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-03-01-preview"
)

response = self.client.embeddings.create(
    input=input,
    model="text-embedding-ada-002"
).data[0].embedding
```

次に、ベクトル化したデータをCosmosDBに格納します。

```python
class CosmosPageObj:
    def __init__(self, 
                content: str, 
                content_vector,):
        self.id = str(uuid.uuid4())
        self.content = content
        self.content_vector = content_vector

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "content_vector": self.content_vector,
        }

    @staticmethod
    def from_dict(dict):
        return CosmosPageObj(dict["id"],
                            dict["content"], 
                            dict["content_vector"])

import os
import azure.cosmos.cosmos_client as CosmosClient

COSMOSDB_URI = os.getenv('COSMOSDB_URI')
COSMOSDB_KEY = os.getenv('COSMOSDB_KEY')
DATABASE_NAME = os.getenv('COSMOSDB_DATABASE_NAME')
CONTAINER_NAME = os.getenv('COSMOSDB_CONTAINER_NAME')

# OpenAIのEmbeddingモデルでベクトル化したデータをCosmosDBに格納
cosmos_page_obj = CosmosPageObj(content="PDF内のテキストデータ", 
                                content_vector=response)

self.client = CosmosClient.CosmosClient(COSMOSDB_URI, {'masterKey': COSMOSDB_KEY})
self.database = self.client.get_database_client(DATABASE_NAME)
self.container = self.database.get_container_client(CONTAINER_NAME)

self.container.upsert_item(data)
```

### CosmosDBに対してベクトル検索

検索はWebアプリケーションなどから行うことが多いため、JavaScriptでの実装例を示します。

```javascript
import { AzureKeyCredential, OpenAIClient } from '@azure/openai';
import {
    CosmosClient,
    Database,
    Container,
} from "@azure/cosmos";

// ベクトル化
console.log('🚀Get embedding from Azure OpenAI.');
const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
const azureApiKey = process.env.AZURE_OPENAI_API_KEY!;
const deploymentId = process.env.AZURE_OPENAI_VEC_DEPLOYMENT_ID!;
const client = new OpenAIClient(
    endpoint,
    new AzureKeyCredential(azureApiKey)
);
const embedding = await client.getEmbeddings(deploymentId, [message]);
const embeddedMessage = embedding.data[0].embedding;

// CosmosDBでベクトル検索
console.log('🚀Search vector from Azure CosmosDB.');
const cosmosClient = new CosmosClient(process.env.COSMOS_CONNECTION_STRING!);
const database = cosmosClient.database(process.env.COSMOS_DATABASE_NAME!);
const container = database.container(process.env.COSMOS_CONTAINER_NAME!);
// similarity scoreが0.88以上のものを取得
const { cosmosItems } = await container.items
    .query({
        query: "SELECT c.content, VectorDistance(c.content_vector, @embedding) AS SimilarityScore FROM c WHERE VectorDistance(c.content_vector, @embedding) > 0.88 ORDER BY VectorDistance(c.content_vector, @embedding)",
        parameters: [{ name: "@embedding", value: embedding }]
    })
    .fetchAll();
for (const item of resources) {
    console.log(`🚀${item.content}, ${item.SimilarityScore} is a capitol \n`);
}

```

ユーザメッセージが「2024年1-3月の日本のGDPは？」という場合、CosmosDB内の以下データが検索されました。
１つ目の類似度スコア：0.8947381295241266
２つ目の類似度スコア：0.8947327649538163

**取得したいドキュメントが検索できました！！！**

また、そのあと検索ドキュメントを使って推論を行うと、以下のように回答してくれました。OpenAIを使ったRAGとしての仕組みとして使えそうです。
```bash
2024年1～3月期の日本の実質GDP成長率は、前期比で-0.5％（年率-2.0％）です。また、名目GDP成長率は前期比で0.1％（年率0.4％）です。
```


::: details コンソールログ
```bash
🚀2024-01~03月GDP, Economic and Social Research Institute
Cabinet Office, Government of Japan
Released 2024.5.16

2024年1～3月期四半期別ＧＤＰ速報（１次速報値）
Quarterly Estimates of GDP for January - March 2024 (First Preliminary Estimates)

令和６年５月１６日
内閣府経済社会総合研究所
国民経済計算部

I. 国内総生産（支出側）及び各需要項目
GDP(Expenditure Approach) and Its Components

1. ポイント
Main Points(Japanese)

[1] ＧＤＰ成長率（季節調整済前期比）
2024年1～3月期の実質ＧＤＰ（国内総生産：2015年基準連鎖価格）の成長率は、▲0.5％（年率▲2.0％）となった。また、名目ＧＤＰの成長率は、0.1％（年率0.4％）となった。

[2] ＧＤＰの内外需別の寄与度
ＧＤＰ成長率のうち、どの需要がＧＤＰをどれだけ増加させたかを示す寄与度でみると、実質国内需要（内需）が、▲0.2％、財貨・サービスの純輸出（輸出－輸入）が、▲0.3％となった。また、名目国内需要（内需）が0.5％、財貨・サービスの純輸出（輸出－輸入）が、▲0.4％となった。

実質ＧＤＰ成長率の推移
2023 1-3: 1.2, 4-6: 1.0, 7-9: 0.2, 10-12: -0.9, 2024 1-3: -0.5

名目ＧＤＰ成長率の推移
2023 1-3: 2.2, 4-6: 2.6, 7-9: 0.7, 10-12: 0.1, 2024 1-3: 0.1

実質ＧＤＰの内外需別寄与度の推移
2023 1-3: 内需 1.2, 外需 0.0, 4-6: 内需 1.0, 外需 0.0, 7-9: 内需 0.3, 外需 -0.1, 10-12: 内需 -0.2, 外需 -0.7, 2024 1-3: 内需 -0.2, 外需 -0.3

名目ＧＤＰの内外需別寄与度の推移
2023 1-3: 内需 2.3, 外需 -0.1, 4-6: 内需 2.7, 外需 -0.1, 7-9: 内需 0.3, 外需 0.4, 10-12: 内需 0.5, 外需 -0.4, 2024 1-3: 内需 0.5, 外需 -0.4, GDP/2024-01~03月GDP_page0.png, 0.8947381295241266 is a capitol 

🚀2024-01~03月GDP, Economic and Social Research Institute
Cabinet Office, Government of Japan
Released 2024.5.16

2024年1～3月期四半期別ＧＤＰ速報（１次速報値）
Quarterly Estimates of GDP for January - March 2024 (First Preliminary Estimates)

令和６年５月１６日
内閣府経済社会総合研究所
国民経済計算部

I. 国内総生産（支出側）及び各需要項目
GDP(Expenditure Approach) and Its Components

1. ポイント
Main Points(Japanese)

[1] ＧＤＰ成長率（季節調整済前期比）
2024年1～3月期の実質ＧＤＰ（国内総生産：2015年基準連鎖価格）の成長率は、▲0.5％（年率▲2.0％）となった。また、名目ＧＤＰの成長率は、0.1％（年率0.4％）となった。

[2] ＧＤＰの内外需別の寄与度
ＧＤＰ成長率のうち、どの需要がＧＤＰをどれだけ増減させたかを示す寄与度でみると、実質国内需要（内需）が、▲0.2％、財貨・サービスの純輸出（輸出－輸入）が、▲0.3％となった。また、名目国内需要（内需）が0.5％、財貨・サービスの純輸出（輸出－輸入）が、▲0.4％となった。

実質ＧＤＰ成長率の推移
2023: 1.2, 1.0, 0.0, -0.9, 0.5
2024: -0.5

名目ＧＤＰ成長率の推移
2023: 2.2, 2.6, 0.7, 0.3, 0.1

実質ＧＤＰの内外需別寄与度の推移
2023: 1.2, 1.0, 0.0, -0.9, 0.5
2024: -0.5

名目ＧＤＰの内外需別寄与度の推移
2023: 2.2, 2.6, 0.7, 0.3, 0.1, GDP/2024-01~03月GDP_page0.png, 0.8947327649538163 is a capitol 
```
:::

# まとめ
Microsoft Build 2024で発表された、CosmosDB for NoSQLのベクトル検索機能について、用途の考察と実装方法を紹介しました。
ベクトル検索は問題なくできており、ベクトル検索だけでよければ、AISearchの代わりにCosmosDBを使えそうです。
RAGの仕組みを構築するにおいて、Azureではさまざまなサービスを組み合わせて用途に応じて使い分けることができるようになってきました。

## その他、今後に期待すること
Azure Functions Extensions for OpenAIもBuildで発表されていました。
まだこちらのExtensionには、CosmosDB for MongoDBのベクトル値格納＆検索しか対応していません。
今後、CosmosDB for NoSQLのベクトル検索にも対応してくれることで、Azure FunctionsとCosmosDB for NoSQLを組み合わせたアプリ開発がさらに便利になると思っています。期待したい...！