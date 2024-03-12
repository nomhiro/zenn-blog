---
title: "Blobに登録されたことを仮想ネットワーク内のFunctionsに通知する仕組み"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "EventGrid", "Functions", "Blob"]
published: false
---

# はじめに

- Azureで、Blobに登録されたドキュメントを、Functionsで整形したうえでCosmosDBやAISearchに取り込む仕組みを考えます。
    EventGridを使う場合はこのような構成になります。
    また、エンタープライズの皆様は、可能な限りパブリックエンドポイントは使わずにプライベートな通信を実現したい場合が多いです。
    **そのため、Functionsのエンドポイントは仮想ネットワーク内に属したプライベートエンドポイントのみを有効にし、サービスエンドポイントは使いたくないという要件を考えます。**
    ![Blob→EventGrid→Functions→CosmosDB](/images/notsupported-eventgrid-to-privateendpoint/2024-01-13-11-53-38.png)
- BlobからのイベントをFunctionsに通知する仕組みはいくつかあります。
  - EventGrid：イベント処理に特化しているため、最も適しています。上記の図の通り。
  - BlobTrigger：トリガーという名前ですが、裏の仕組みはFunctionsから定期的にポーリングする仕組みです。

それぞれの仕組みについて、実現可能性と設定方法を後述します。

# EventGridからVNet内のFunctionsに通知できない

- EventGridは、Azureのリソースのイベントを受け取って、サブスクリプションに登録されたエンドポイントに通知するサービスです。
- **ただし、以下公式ドキュメントにあるように、EventGridから送信する通信はサービスタグのみ対応しており、仮想ネットワーク内のプライベートエンドポイントには通知できません。。。**
    サービスエンドポイントを使う方が多いとは思いますが、セキュリティ面を懸念するエンタープライズの皆様は、可能な限りプライベートエンドポイントを使いたいという要件が多いため、この仕様は残念です。。プライベートエンドポイントにイベントを送信する仕様が追加されることを期待します。
　[Microsoft公式ドキュメント EventGridのネットワークセキュリティ](https://learn.microsoft.com/ja-jp/azure/event-grid/network-security#service-tags)

    ![EventGridからVNet内のFunctionsに通知できない](/images/notsupported-eventgrid-to-privateendpoint/2024-01-13-12-10-17.png)

# BlobTriggerを使ったFunctionへの通知

- BlobTriggerはEventGridとは仕組みが異なり、Functionsから定期的にポーリングする仕組みです。定期的にBlobStorageのログとコンテナスキャンを行うことで機能する仕組みになっています。
- 致命的なのは、公式ドキュメント[AzureBlobStorageトリガーのポーリングと待ち時間](https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-bindings-storage-blob-trigger?tabs=python-v2%2Cisolated-process%2Cnodejs-v4&pivots=programming-language-python#polling-and-latency)に以下のように書かれている点です。
    **つまり、ログの欠落が発生した場合は、BlobTriggerによる通知が行われない可能性があるということです。**
:::message
[ストレージ ログは "ベスト エフォート" ベースで作成](https://learn.microsoft.com/ja-jp/rest/api/storageservices/About-Storage-Analytics-Logging)されます。 すべてのイベントがキャプチャされる保証はありません。 ある条件下では、ログが欠落する可能性があります。
:::
- そのため、以下の回避策をとるように書かれています。
    ![回避策](/images/notsupported-eventgrid-to-privateendpoint/2024-01-13-12-30-30.png)

# 回避策を考えてみる

- PrivateEndpointを構成しているFunctionにイベントを通知したい場合、EventGridを使えません。そしてBlobTriggerは、ログの欠落が発生した場合に通知が行われない可能性があるため、本番向けシステムには使いづらいです。
- これを回避できるソリューションを二つ考えてみました。

## 1. Blobにドキュメントを登録する際に、Queueにメッセージを登録し、QueueトリガーでFunctionを動かす。
- 以下のように[Microsoftドキュメント](https://learn.microsoft.com/ja-jp/rest/api/storageservices/About-Storage-Analytics-Logging)にも書かれている回避策です。![回避策 queue](/images/notsupported-eventgrid-to-privateendpoint/2024-01-13-12-35-09.png)
    ![queue-to-functions](/images/notsupported-eventgrid-to-privateendpoint/2024-01-13-12-45-27.png)
- BlobStorageにドキュメントを登録する仕組みがすでにある場合に向いています。その仕組みにQueue登録処理を追加することで実現できます。

## 2. Functionを定期実行しBlobChangeFeedを取得し、Blobファイルの更新を処理する。
- BlobChangeFeedはFunctionのトリガーに体操していないため、FunctionからポーリングしてBlobChangeFeedを自前のロジックで取得します。
- BlobChangeFeedで保存される.avroファイルを読み取り、イベントごとにCreated, Changed, Deletedのステータスがあるため、各イベントごとの処理を書くことができます。

## 3. EventGridを使いEventGridからStorageQueueに登録する。そして、StorageQueueトリガーでFunctionを動かす。
- この場合、EventGridからStorageQueueの通信はサービスエンドポイント経由のためパブリックアクセスですが、StorageQueue側の設定で、通知するEventGridを限定することができます。
    ![eventGrid-queue-to-functions](/images/notsupported-eventgrid-to-privateendpoint/2024-01-13-12-54-06.png)
 - BlobStorageにドキュメントを登録する仕組みがない場合はこちらのやり方が向いています。
