---
title: "EventGridがMicrosoftサービス（SPO,Teams等）からのイベントに対応（PublicPreview）"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "EventGrid","SharePoint","Teams"]
published: false
---

# EventGridがSPO,TeamsなどのMicrosoftサービスからのイベントに対応（PublicPreview）

## パブリックプレビューの概要
気が付くのが遅れましたが、こちらの更新情報に上がっていました。
[Azure更新情報の公式サイト](https://azure.microsoft.com/ja-jp/updates/event-grid-graph-api-public-preview/)
![Azure更新情報の公式サイト](/images/eventgrid-from-microsoft-service/2023-12-27-23-15-18.png)

## 何が嬉しいか
- OpenAIを使ったRAGシステムを構築するためには、裏側のデータのため方が非常に重要です。**EventGridを使うとデータの更新を検知して、更新されたデータを取得し、データの加工やAISearchへのインデックス登録を行うことができます。つまり、データが登録/更新されれば自動でRAGシステムの裏側のデータ更新が行われるため、運用面での負荷を軽減することができます。**
- 企業では、Microsoftサービス、とくにデータ格納先はSharePointを利用していることが多いと思います。
- 今までは、BlobStroageなどのAzureサービスからのイベントを受け取ることができましたが、Microsoftサービスからのイベントを受け取ることができなかったため、LogicAppsなどを利用していました。
- 今回のアップデートにより、Microsoftサービスからのイベントを受け取ることができるようになり、よりシンプルな構成でイベントを受け取れます！
![](/images/eventgrid-from-microsoft-service/2023-12-27-23-41-31.png)

## 今後

実際にどのような設定で利用できるかは今後検証していきたいと思います。