---
title: "MTG動画をナレッジ活用できるように議事録にしよう！"
emoji: "🐕"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# はじめに
人ができることをAIに置き換える際には、「その人のナレッジをいかにデータ化しておくか」が鍵となります。
日々の業務では、MTGを頻繁に実施して、個人の知見や意見をもとに何らかの意思決定を行っているはずです。どのリモート会議ツールもMTGの録画機能を持っているため、MTGの動画を録画しておくことは簡単です。
MTGに参加する人のナレッジを、MTG動画から抽出するために、まずは動画から議事録作成を行ってみます。

# リソースの作成

## Azure Video Indexer

![](/images/generate-minutes-from-mtg-video/2024-11-17-21-18-06.png)

StorageAccountの設定
![](/images/generate-minutes-from-mtg-video/2024-11-17-21-12-51.png)

![](/images/generate-minutes-from-mtg-video/2024-11-17-21-19-00.png)

![](/images/generate-minutes-from-mtg-video/2024-11-17-21-19-11.png)

![](/images/generate-minutes-from-mtg-video/2024-11-17-21-19-44.png)

作成したリソース
:::message alert
エラーメッセージが２つあります。
- このアカウントを Azure ストレージ アカウントに接続するには、マネージド ID ロールの割り当てが必要です。
- Azure OpenAI はまだ接続されていません。Azure OpenAI リソースにロールを割り当てる必要があります。

**それぞれに、「ロールを割り当て」というボタンがありますので、そちらをクリックしてVideo-IndexerのマネージドIDをStorageAccountとOpenAIに割り当てます。**
:::
![](/images/generate-minutes-from-mtg-video/2024-11-17-21-22-06.png)

Azure ストレージアカウントにマネージドIDを割り当てることでエラー解消
![](/images/generate-minutes-from-mtg-video/2024-11-17-21-25-56.png)

Azure OpenAIにマネージドIDを割り当てることでエラー解消
![](/images/generate-minutes-from-mtg-video/2024-11-17-21-26-08.png)