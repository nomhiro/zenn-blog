---
title: "BlobStorageのChangeFeedトリガーでFunctionを起動する"
emoji: "🎃"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "EventGrid", "Queue", "Functions", "BlobStorage"]
published: false
---

# はじめに

BlobStorageにドキュメントを保管したあとに、そのドキュメントを整形したり他リソースへの登録処理などを行うためには、BlobStorageにドキュメントが格納されたことをトリガーにしてFunctionを起動する必要があります。
BlobStorageにドキュメントが格納されたことをトリガーにしてFunctionを起動する方法はいくつかあります。
1,2は以前の記事で設定方法などをまとめてあります。今回は3の方法を整理します。
1. EventGridを使ってBlobStorageのイベントをFunctionに通知する。（BlobStorageイベント）
https://zenn.dev/nomhiro/articles/notsupported-eventgrid-to-privateendpoint
1. ChangeFeedを使ってBlobStorageの変更をFunctionに通知する
https://zenn.dev/nomhiro/articles/blob_queue-to-function
1. **BlobStorageのイベントをQueueに通知し、QueueTriggerでFunctionを起動する。**

:::message alert
1.の方法でBlobStorageのイベントをEventGridを使い、**プライベート通信で**Functionsに通知することはできません。
こちらの記事で説明してますのでご参考までに。
https://zenn.dev/nomhiro/articles/notsupported-eventgrid-to-privateendpoint
![EventGridからPrivateでFunctionにイベントを通知できない](/images/blob-to-queue-to-function/2024-01-13-17-43-29.png)
:::

# BlobStorageのChangeFeedの仕組み
https://learn.microsoft.com/ja-jp/azure/storage/blobs/storage-blob-change-feed?tabs=azure-portal

ChangeFeedレコードは、ストレージアカウント内のコンテナにBlobとして保存されます。変更イベントは、変更から数分以内に変更フィードログに書き込まれ、使用可能になります。

# 必要なリソースと実装箇所
プライベート通信でTriggerするように構築します。
- BlobStorage
  ![BlobStorage](/images/blob_change_feed_trigger/2024-02-25-18-26-25.png)
  - PrivateEndpoint
  ![BlobStorage PrivateEndpoint](/images/blob_change_feed_trigger/2024-02-25-18-26-51.png)
- Function
  - PrivateEndpointとVnet統合を設定
  ![Function PrivateEndpointとVnet統合](/images/blob_change_feed_trigger/2024-02-25-20-14-26.png) 

# 実際に動作確認します。

### BlobStoageのChangeFeedを有効にする

「データ管理 > データ保護」の画面から、「Blobの変更フィードを有効にする」にチェックを入れます。
ChangeFeedのログを永続的に残す場合は「すべてのログを保持する」を選択し、C保持期間を過ぎたらログを削除する場合は「変更フィードログを削除するまでの期間(日数)」を選択し、保持期間を指定します。
ここでは「変更フィードログを削除するまでの期間(日数)」を選択し、保持期間を7日に設定します。
![BlobStoageのChangeFeedを有効にする](/images/blob_change_feed_trigger/2024-02-25-18-25-30.png)

有効にした後にBlobコンテナを参照すると、「$blobchangefeed」というコンテナが作成されていることがわかります。
![$blobchangefeedコンテナ](/images/blob_change_feed_trigger/2024-02-25-20-15-50.png)