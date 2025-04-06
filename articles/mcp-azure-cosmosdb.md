---
title: "Azure CosmosDB MCPサーバ を使って、自然言語でデータ取得してみよう！"
emoji: "🎉"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "AI", "MCP", "CosmosDB", "Claude"]
published: false
---

# はじめに
この頃、MCP（Model Context Protocol）の展開が非常に盛んになっています。
MCPとは、アプリケーションがLLMにコンテキストを提供する方法を標準化するオープンプロトコルです。つまり、**LLMが他のツールを呼び出しデータ取得やツール実行を行うためのプロトコル**です。
詳しくはこちらの記事を参考にしてください！
https://zenn.dev/nomhiro/articles/mcp-azure-ai-foundry-use-vercel-ai-sdk
とくにこちらの記事が非常に詳細に、例とともに解説されているので分かりやすいです。
https://zenn.dev/chips0711/articles/e71b088f26f56a


この記事では、**CosmosDB MCP Server** を試してどのような利用シーンがあるのか探ってみます。
GitHubリポジトリで、Azure CosmosDBをMCPサーバとする実装が公開されています。
https://github.com/AzureCosmosDB/azure-cosmos-mcp-server


# PoC🚀
それでは試してみましょう。

## 利用シナリオ
CosmosDB にクルマへのお客様からのフィードバック情報が登録されているとします。PoCシナリオとしては、この**フィードバックデータを自然言語で取得しながら分析するシーン**を想定してみましょう。

## 前提
- Node.js 14以上 インストール済み
  - https://nodejs.org/ja/download/
- Claude Desktop インストール済み
  - https://claude.ai/download
- Azure サブスクリプションを持っていること
  - https://azure.microsoft.com/ja-jp/pricing/purchase-options/azure-account/

## CosmosDB の準備

:::details CosmosDBアカウントとコンテナの作成
アカウントの作成
![](/images/mcp-azure-cosmosdb/2025-04-06-14-57-18.png)

![](/images/mcp-azure-cosmosdb/2025-04-06-15-10-17.png)

データベースとコンテナの作成
![](/images/mcp-azure-cosmosdb/2025-04-06-15-46-09.png)
:::



以下のような、ユーザからのフィードバック情報が登録されているコンテナーを想定します。
※Copilotに生成してもらったデータなので、実際のデータではありません。
- database名：feedback
- container名：customer-feedback
- partition key：/carModel

```json
[
  {
    "id": "1",
    "carModel": "プリウス",
    "manufacturer": "Toyota",
    "rating": 5,
    "reviewText": "燃費が非常に良く、環境にも優しい。運転もしやすく、家族全員におすすめです。",
    "reviewDate": "2025-03-25T09:15:00Z",
    "location": "東京",
    "tags": ["燃費", "環境", "運転のしやすさ"],
    "sentimentScore": 0.95
  },
  {
    "id": "2",
    "carModel": "プリウス",
    "manufacturer": "Toyota",
    "rating": 4,
    "reviewText": "コンパクトで取り回しが良いが、加速性能がもう少し欲しかった。",
    "reviewDate": "2025-03-28T14:30:00Z",
    "location": "大阪",
    "tags": ["操作性", "加速性能"],
    "sentimentScore": 0.75
  },
  {
    "id": "3",
    "carModel": "フィット",
    "manufacturer": "Honda",
    "rating": 4,
    "reviewText": "小回りが利く点が魅力。室内空間も広く感じられ、普段使いに最適です。",
    "reviewDate": "2025-04-01T11:00:00Z",
    "location": "名古屋",
    "tags": ["取り回し", "室内空間", "燃費"],
    "sentimentScore": 0.80
  }
]
```

## MCPサーバの準備

こちらのGitHubリポジトリをCloneします。
https://github.com/AzureCosmosDB/azure-cosmos-mcp-server

Cloneしたプロジェクトのルートフォルダに.envファイルを作成し、接続するCosmosDBの情報を記載します。
GitHubを見ていたら、miyake-sanがIssueを出して環境変数化してくださっていました。ありがたし....!!

```bash
COSMOSDB_URI="Azure Cosmos DB の URI"
COSMOSDB_KEY="Azure Cosmos DB の APIキー"
COSMOS_DATABASE_ID="データベース名（feedback）"
COSMOS_CONTAINER_ID="コンテナ名（customer-feedback）"
```

Cloneしたプロジェクトのルートフォルダで以下のコマンドを実行して、必要なライブラリをインストールします。
```bash
npm install
```

プロジェクトをコンパイルします。distフォルダにコンパイルされたファイルが生成されます。
```bash
npm run build
```

もし、MCPサーバを手動で立てたい場合は、コンパイルしたファイルでサーバーを起動します。
:::details MCPサーバ手動起動
distフォルダに移動し、サーバーを起動します。
```bash
cd dist
npm start
```

サーバーが起動したら、以下のようなメッセージが表示されます。
```bash
Azure Cosmos DB Server running on stdio
```
:::

## Claude Desktop で稼働確認しましょう

Claude Desktop で MCPサーバを起動する設定をする必要があります。
そのあと、チャットしてみましょう！

### Claude Desktop の設定

Claude Desktop 起動時に、コンパイルしたファイルでMCPサーバを起動するように設定します。

Claude Desktop の「ファイル」->「設定」の画面へ。
![](/images/mcp-azure-cosmosdb/2025-04-06-18-43-05.png)

開発者タブで、「構成を編集」すると、設定ファイルの場所が表示されます。
![](/images/mcp-azure-cosmosdb/2025-04-06-18-44-16.png)

このclaude_desktop_config.jsonファイルを以下のように編集します。
![](/images/mcp-azure-cosmosdb/2025-04-06-18-44-42.png)

```json
{
  "mcpServers": {
    "cosmosdb": {
      "command": "node",
      "args": [ "C:/Users/AdmUser/Documents/mcp-azure-cosmosdb/azure-cosmos-mcp-server/dist/index.js" ],
      "env": {
        "COSMOSDB_URI": "Azure Cosmos DB の URI",
        "COSMOSDB_KEY": "Azure Cosmos DB の APIキー",
        "COSMOS_DATABASE_ID": "feedback",
        "COSMOS_CONTAINER_ID": "customer-feedback"
      }
    }
  }
}
```

Claude Desktopを再起動します。一度終了しましょう。
※Desktopを閉じるだけでは再起動にならず、設定ファイルが読み込まれません。
![](/images/mcp-azure-cosmosdb/2025-04-06-18-46-22.png)

Claude Desktop を起動しなおすと、MCPサーバが起動され、利用可能なMCPツールにCosmosDBツールが追加されています。
![](/images/mcp-azure-cosmosdb/2025-04-06-18-47-41.png)


### それでは、試してみましょう。
```
プリウスのフィードバックデータを見たいです。
```

以下のような結果となりました。
![](/images/mcp-azure-cosmosdb/2025-04-06-18-53-22.png)
![](/images/mcp-azure-cosmosdb/2025-04-06-18-53-40.png)

- まず最初に、'Prius'というキーワードでフィルターしたため、検索結果が0件でした。
- そのため次に、'Toyota Prius'または'プリウス'でフィルターするように**CosmosDBのクエリが生成**されました。
ですが、フィールド名が'carModel'であるにもかかわらず、'model'でクエリが生成されていますね。。もちろん検索結果は0件のままです、
- そのため、次はプリウスのフィルターが無くなり、**'トヨタ'または'Toyota'で製造元をフィルターするクエリが生成**されました。これで**トヨタのフィードバックデータが取得**されています。
- そして最後に、取得したデータからプリウスのユーザフィードバックデータをもとに推論しています。

**本来は、carModelフィールドでフィルターしてほしいのですが、MCPサーバの実装に改善の余地がありそうですね！**

# まとめ
MCPサーバを利用して、自然言語でデータ取得することができました。
MCPサーバを利用することで、自然言語でデータ取得することができるようになります。これにより、ユーザはデータベースのクエリを意識せずに、自然な言葉で情報を取得できるようになります。

データベースのクエリを自然言語で行うことができるため、データベースの専門知識がないユーザでも簡単に情報を取得できることがメリットかと思います。
データの分析では、BIツールを使いVisualizeすることが多いと思います。BIで見える化しつつ、補足ツールとしてMCPサーバを利用することで、分析の幅が広がるかもしれませんね。