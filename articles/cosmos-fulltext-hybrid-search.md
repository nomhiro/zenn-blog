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

::: message alert
2024/11/22時点では、サポートされている言語は英語 (言語が "en-us" に指定されているもの) のみです。
:::
コスト効率の良い、高いSLAとスケーラビリティを持つAzure CosmosDBにおいて、より検索精度を高められるようになるため、今後のCosmosDBの利用がますます期待されます。
Azure AI Searchの検索インデックスサービスもあるので、使い分けになってくると思います。
データベースに保管すべきデータならCosmosDB、インデックス化したいデータなのであればAzure AI Searchを使うといった使い分けができると思います。ただし、コスト面やSLAの面でAzure CosmosDB for NoSQLが有利ですので、機能と非機能要件、そしてコストを考慮した選定が必要です。

※ベクトル検索の詳細はこちらを参照ください。
https://zenn.dev/nomhiro/articles/cosmos-nosql-vector-search

::: message alert
バックアップできる？
:::

# フルテキスト検索とハイブリッド検索を使おう

## 前提


## 検索対象のデータ
以下のようなデータを想定します。
- contentフィールド：フルテキスト検索対象のデータ。
- content_vectorフィールド：contentをベクトル化したベクトル値
![](/images/cosmos-fulltext-hybrid-search/2024-11-26-22-50-50.png)

## フルテキスト検索とハイブリッド検索機能の有効化

CosmosDBアカウントに対して一度機能を有効にすると、その後無効にすることはできませんのでご注意ください。

既存のCosmosDBのアカウントに対してフルテキスト検索とハイブリッド検索機能を有効化します。
※既存のCosmosDBアカウントでは、すでにベクトル検索の機能「Vector Search for NoSQL API」は有効化されています。

CosmosDBのアカウントの機能ページにて、機能「Full-Text & Hybrid Search for NoSQL API (preview)」を有効にします。
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-32-10.png)

![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-31-13.png)

11/22時点ですと、以下エラーになりましたが、
```
Enabling Full-Text & Hybrid Search for NoSQL API (preview)
Invalid capability EnableNoSQLFullTextSearch.
ActivityId: 63f44a95-665f-43a4-a62c-48af2ac6f02e, Microsoft.Azure.Documents.Common/2.14.0
```
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-33-52.png)

**11/26時点では、有効化できました！！！！！！！**
![](/images/cosmos-fulltext-hybrid-search/2024-11-26-22-13-02.png)

::: message alert
2024/11/26時点では、JapanEastリージョンのアカウントで有効化できました。
※具体的な利用可能リージョンの記載は見つかりませんでした。
Dev Blogのページや機能の有効化時のメッセージには以下のように記載されています。「2025 年 1 月初旬に完全にロールアウト」
まだすべてのリージョンで使えるわけではないようです。
![](/images/cosmos-fulltext-hybrid-search/2024-11-22-03-53-11.png)
![](/images/cosmos-fulltext-hybrid-search/2024-11-26-22-18-54.png)
:::

## ベクトルポリシーの設定

ベクトルポリシーが有効化された既存のCosmosDBアカウントを使っているため、以下のように設定済みです。
embeddingのlargeモデルを使う想定だったため、ベクトル次元数は3072になっています。
また、diskANNではなくquantizedFlatを使っています。データ量が多くなる場合は、diskANNを使うといいでしょう。
![](/images/cosmos-fulltext-hybrid-search/2024-11-26-22-30-48.png)

設定方法はこちらを参照してください。
https://zenn.dev/nomhiro/articles/cosmos-nosql-vector-search

※diskANNの詳しい情報はこちら
https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/

## フルテキストポリシー

※冒頭で触れましたが、2024/11/26時点では、英語のみのサポートです。
![](/images/cosmos-fulltext-hybrid-search/2024-11-26-22-46-07.png)

contentフィールドに対してフルテキストポリシーを設定します。
**ベクトルポリシーとは異なり、フルテキストポリシーは設定後もフィールド追加や変更が可能ですね！！ありがたい！！！**
![](/images/cosmos-fulltext-hybrid-search/2024-11-26-22-53-06.png)
