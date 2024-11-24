---
title: "Azure CosmosDB for NoSQLのフルテキスト検索とハイブリッド検索"
emoji: "😎"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "CosmosDB", "NoSQL", "VectorSearch", "HybridSearch"]
published: false
---

# はじめに

Microsoft Ignite 2024にて、Azure CosmosDB for NoSQLにおいてフルテキスト検索とハイブリッド検索がサポートされることが発表されました。（Public Preview）
https://devblogs.microsoft.com/cosmosdb/new-vector-search-full-text-search-and-hybrid-search-features-in-azure-cosmos-db-for-nosql/

Microsoft Learnのページはこちら
https://learn.microsoft.com/ja-jp/azure/cosmos-db/gen-ai/full-text-search

Azure CosmosDB for NoSQLにベクトル検索がすでにあります。そのため、CosmosDB for NoSQLでは、「フルテキスト検索」「ベクトル検索」「ハイブリッド検索」がサポートされたことになります。
::: message
2024/11/22時点では、サポートされている言語は英語 (言語が "en-us" に指定されているもの) のみです。
:::
コスト効率の良い、高いSLAとスケーラビリティを持つAzure CosmosDBにおいて、より検索精度を高められるようになるため、今後のCosmosDBの利用がますます期待されます。
Azure AI Searchの検索インデックスサービスもあるので、使い分けになってくると思います。
データベースに保管すべきデータならCosmosDB、インデックス化したいデータなのであればAzure AI Searchを使うといった使い分けができると思います。ただし、コスト面やSLAの面でAzure CosmosDB for NoSQLが有利ですので、機能と非機能要件、そしてコストを考慮した選定が必要です。

※ベクトル検索の詳細はこちらを参照ください。
https://zenn.dev/nomhiro/articles/cosmos-nosql-vector-search


# フルテキスト検索とハイブリッド検索を使おう

## 前提


## 検索対象のデータ


## フルテキスト検索とハイブリッド検索機能の有効化

CosmosDBアカウントに対して機能を有効にすると、無効にすることはできませんのでご注意ください。

### 既存のCosmosDBアカウントに対する有効化
既存のCosmosDBのアカウントに対してフルテキスト検索とハイブリッド検索機能を有効化します。
※既存のosmosDBアカウントでは、すでにベクトル検索の機能「Vector Search for NoSQL API」は有効化されています。

CosmosDBのアカウントの機能ページにて、機能「Full-Text & Hybrid Search for NoSQL API (preview)」を有効にします。
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-32-10.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-31-13.png)

エラーになります。
```
Enabling Full-Text & Hybrid Search for NoSQL API (preview)
Invalid capability EnableNoSQLFullTextSearch.
ActivityId: 63f44a95-665f-43a4-a62c-48af2ac6f02e, Microsoft.Azure.Documents.Common/2.14.0
```
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-33-52.png)

::: message alert
2024/11/22時点では、JapanEastのリージョンでは有効化できないようです。
※具体的な利用可能リージョンの記載は見つかりませんでした。
Dev Blogのページにも以下のように記載されています。2025年1月にはリージョン制限がなくなるようですのでしばらく待ちましょう。
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-53-11.png)
:::

### 新規のCosmosDBアカウントでの有効化
NorthCentralUSリージョンでCosmosDBアカウントを作成します。
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-04-35-25.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-45-17.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-45-29.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-45-38.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-45-47.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-45-59.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-46-12.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-48-49.png)

では次に、作成したアカウントに対して、フルテキスト検索とハイブリッド検索機能を有効化します。
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-49-22.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-49-33.png)