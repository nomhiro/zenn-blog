---
title: "Queueを介してBlob更新をFunctionにプライベート接続でイベント通知する方法"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "EventGrid", "Queue", "Functions", "Blob"]
published: false
---

# はじめに

[こちらの記事](https://zenn.dev/nomhiro/articles/notsupported-eventgrid-to-privateendpoint)で紹介していますが、BlobStorageのイベントをEventGridを使い、プライベート通信でFunctionsに通知することはできません。
![EventGridからPrivateでFunctionにイベントを通知できない](/images/blob-to-queue-to-function/2024-01-13-17-43-29.png)

上記の問題に対処するために、以下の回避策を設定・実装します。
BlobStorageにドキュメントを格納したのち、Queueに登録したドキュメント名を含むメッセージを登録します。その後、QueueTriggerでFunctionを実行し、ドキュメント名からドキュメントを取得します。
![回避策1_Queue利用](/images/blob-to-queue-to-function/2024-01-13-17-48-36.png)

# 必要なリソースと実装箇所
構築のためには以下のリソースが必要です。
※左側の「ドキュメントを格納するアプリケーション」は作成はせずに、手動で仮定して稼働確認します。
- StorageAccount
  - Blob
  - Queue
- FunctionApp
  - PrivateEndpoint
  - python実装したソースコード
      1. QueueTriggerで実行
      2. Queueのメッセージに含まれたBlobのドキュメント名を取得
      3. ドキュメント名からドキュメントを取得する。

# リソースの作成

## StorageAccountの作成

1. StorageAccountを作成します。
    その他の設定はデフォルトのままでOKです。
    ※セキュリティを考慮したエンタープライズ向けの記事ですので、サービスエンドポイントは使わずプライベートエンドポイントを設定しました。
    ![StorageAccount作成_01](/images/blob-to-queue-to-function/2024-01-13-18-15-17.png)

2. 作成したStorageAccountのネットワーク画面から、接続文字列を控えます。この接続文字列は、後ほどFunctionの環境変数に設定します。
    ![StorageAccount作成_02](/images/blob_queue-to-function/2024-01-16-20-54-22.png)

### Blobコンテナの作成

1. 作成したStorageAccountのBlobコンテナ画面から作成
    ![Blobコンテナ作成_01](/images/blob-to-queue-to-function/2024-01-13-18-10-05.png)
2. コンテナ名を入力し作成
    ![Blobコンテナ作成_02](/images/blob-to-queue-to-function/2024-01-13-18-21-41.png)

### Queueの作成

1. 作成したStorageAccountのQueue画面から作成
    ![Queue作成_01](/images/blob-to-queue-to-function/2024-01-13-18-23-02.png)
2. Queue名を入力し作成
    ![Queue作成_02](/images/blob-to-queue-to-function/2024-01-13-18-23-58.png)


## CosmosDBのコンテナを作成

CosmosDBに、データベースとコンテナを作成します。
ここで設定したデータベース名とコンテナ名は、FunctionのPythonソースコードに記載しますので控えておきましょう。
![CosmosDBにコンテナを作成](/images/blob_queue-to-function/2024-01-13-21-13-25.png)

## Functionの作成

1. Functionリソースを作成する。
    ランタイム：Python
    OS:Linux
    ホスティング：Function Premium
    ::: message alert
    Functionにプライベートエンドポイントを設定するためには、Premiumプランを選択する必要があります。
    ただし、Premiumプランはインスタンスが常時起動しているため、コストがかかります。
    2023年12月あたりに発表され、2024年にリリースされる見込みである、"FlexConsumptionプラン"が利用できるようになれば、従量課金のプランでPrivateEndpointを設定できるようになると思います。
    :::
    ![Function作成_01](/images/blob-to-queue-to-function/2024-01-13-18-29-28.png)

2. FunctionのVnet統合を設定する。
    **FunctionがQueueTriggerする仕組みは、Functionからのポーリングする仕組みになっています。そのため、QueueのStorageAccountのプライベートエンドポイントに接続できる仮想ネットワーク内にFunctionを配置する必要があります。**
   1. 払いだされたFunctionリソースのネットワーク画面から、仮想ネットワーク統合を選択する。
   ※1. のFunctionを払い出す際の画面で設定することもできます。
   ![Function作成__Vnet統合_01](/images/blob_queue-to-function/2024-01-16-21-02-26.png)
   2. 仮想ネットワーク統合の追加をクリック
   ![Function作成__Vnet統合_02](/images/blob_queue-to-function/2024-01-16-21-50-42.png)
   3. サブネットを設定して保存
   ![Function作成__Vnet統合_03](/images/blob_queue-to-function/2024-01-16-21-54-09.png)

## Function上で動くPythonコードの実装
QueueTriggerで実行されるPythonコードを実装します。
まずQueueメッセージに含まれるBlobドキュメント名を取得し（）、そのドキュメント名からBlobドキュメントを取得します。
取得したBlobドキュメントの内容をCosmosDBに登録します。

```python
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as Exceptions
from azure.storage.blob import BlobServiceClient

from logging import getLogger
import os, uuid

logging = getLogger(__name__)

COSMOS_ACCOUNT_URI = os.environ['COSMOS_ACCOUNT_URI']
COSMOS_ACCOUNT_KEY = os.environ['COSMOS_ACCOUNT_KEY']
COSMOS_DATABASE_NAME = 'shrkmn-doc'
COSMOS_CONTAINER_NAME = 'shrkmn-doc'
BLOB_CONTAINER_NAME = 'shrkmn-doc-container'

blob_connection_string = os.getenv("AZURE_STORAGE_ACCESS_URL")
storage_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

app = func.FunctionApp()

@app.function_name(name="shrkmn_doc_func")
@app.queue_trigger(arg_name="azqueue", queue_name="shrkmn-doc-queue",
                               connection="AZURE_STORAGE_ACCESS_URL") 
def shrkmn_doc_func(azqueue: func.QueueMessage):
    #QueueのメッセージにBlobドキュメント名が格納される
    blob_doc_name = azqueue.get_body().decode('utf-8')
    logging.info('blob_doc_name: %s', blob_doc_name)
    
    #Blobドキュメントの内容を取得する
    try:
        logging.info('get document content of blob storage.')
        blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string,storage_access_key)
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=blob_doc_name)
        downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
        blob_text = downloader.readall()
        logging.info('blob_text: %s', blob_text)

    except Exception as ex:
        logging.error('Exception: %s', ex)

    #CosmosDBに登録する
    #CosmosDBClientを作成
    client = cosmos_client.CosmosClient(COSMOS_ACCOUNT_URI, {'masterKey': COSMOS_ACCOUNT_KEY}, user_agent="AssistantApp", user_agent_overwrite=True)

    try:
        logging.info('create item for cosmosdb.')
        #CosmosDBに登録するitemを定義
        #idにはuuidを設定
        item = {
            "id": str(uuid.uuid4()),
            "content": blob_text
        }
        logging.info('item: %s', item)
        
        #CosmosDBのデータベースを取得
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        #CosmosDBのコンテナーを取得
        container = database.get_container_client(COSMOS_CONTAINER_NAME)

        #CosmosDBに登録する
        container.create_item(body=item)
    
    except Exceptions.CosmosHttpResponseError as e:
        logging.error('CosmosHttpResponseError: %s', e.message)
    
    logging.info('finish function.')
```

ローカル環境で実行する場合、.envファイルに環境変数の定義が必要です。
```bash
COSMOS_ACCOUNT_URI="COSMOSアカウントのURI"
COSMOS_ACCOUNT_KEY="COSMOSアカウントのキー"
AZURE_STORAGE_ACCESS_URL="StorageAccountの接続文字列"
AZURE_STORAGE_ACCESS_KEY="StorageAccountのアクセスキー"
```

## FunctionにPythonコードをデプロイ
VSCodeのAzure Functions拡張機能を使い、FunctionにPythonコードをデプロイします。
1. AzureFunction拡張機能タブから、Functionアイコンをクリックし、「Deploy to Function App」を選択。
    ![Functionデプロイ_01](/images/blob_queue-to-function/2024-01-16-22-29-59.png)
2. デプロイ先のFunctionを選択。
    ![Functionデプロイ_02](/images/blob_queue-to-function/2024-01-16-22-31-57.png)

## 稼働確認
1. BlobStorageにこのようなサンプルドキュメントを格納。
    ![サンプルファイル](/images/blob_queue-to-function/2024-01-16-22-34-45.png)
    ![Blob_file格納](/images/blob_queue-to-function/2024-01-16-22-33-53.png)
2. Queueにファイル名（ここでは「sample-blob.txt」）をメッセージとして登録。
    ![Queueにメッセージ登録](/images/blob_queue-to-function/2024-01-16-22-37-04.png)
3. QueueTriggerでFunctionが動き、CosmosDBにアイテムが作成されることを確認。
    contentフィールドに、BlobStorageに登録したドキュメントの内容が格納されています。
    ![CosmosDBにアイテムが作成される](/images/blob_queue-to-function/2024-01-16-22-46-11.png)

これで、Queueメッセージを介してBlobStorageのドキュメント更新をFunctionに通知することができました。

# まとめ
今回の構築で、BlobStorageのドキュメント更新をFunctionに通知することができました。
ここの実装ではBlobStorageのドキュメントの内容をそのままCosmosDBに登録していますが、実際のシステムでは、ドキュメントの内容を加工して登録することが多いと思います。
OpenAIのRAGシステムを構築する場合、OpenAIが推論しやすい形式に変換したりする処理を実装することが望ましいです。
もともとのドキュメントはBlobに格納され、加工されたドキュメントはCosmosDBに格納するというように、BlobとCosmosDBで保管するデータの役割を分けることができます。