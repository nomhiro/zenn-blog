---
title: "GPT4VでAzure構成図からBicepコードを生成してみる"
emoji: "💪"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["GPT4V", "Bicep", "Azure"]
published: false
---


# はじめに
GPT-4Vが出る前のGPT3やGPT4で、drawioやsvgで書かれた構成図のメタデータを使って何とかBicepコードを生成できないかと試していましたが、GPT3やGPT4がメタデータを理解できず、上手くいかなかったです。

すきやねんAzureの会で知ったのですが、MS山口さんがGPT4-Vを使ってAzure構成図からARMテンプレートを生成するという記事を書かれていました。
https://qiita.com/shyamagu/items/556f08282a91000c6b14


それ！やりたかったやつ！となりましたので、Bicep版として試してみます。


# 構成図
以下の構成図を使って、Bicepコードを生成してみます。VSCodeのdrawio拡張機能で作成した構成図です。
![](/images/bicep-from-archi-image-poweredbyopenai/2024-03-30-09-32-47.png)


# GPT4VでBicepコードを生成

### システムプロンプト

システムプロンプトは以下のように設定します。
Bicepコードは、個々のリソースごとのBicepファイルと、それを参照するmain.bicepファイル、パラメータファイルの3つに分割して生成します。

**上記の記事のシステムプロンプトに、Bicepファイルを分割する指示と、各リソースに対する制約事項を追加してみました。**

```text
あなたはAzureのインフラストラクチャの専門家です。描画されたAzureリソースを作成するためのBicepコードを作成してください。
各リソース名には、"shrkm-"という文字列に続けて、リソースを表す文字列と、都度ランダムな文字列も含めてください。
例：shrkm-functions-dfiweofsdf
Bicepコードは、個々のリソースごとのBicepファイルと、それを参照するmain.bicepファイル、パラメータファイルの3つに分割して生成しなさい。

# 制約事項
- パラメータファイルには、デプロイ時に外部指定するパラメータを記述すること（リージョン情報）
- StaticWebAppのリージョンは"eastasia"とすること
- StorageAccountのリソース名は、数字と小文字英字のみにすること
- StorageAccountのリソース名は、take()関数を使って24文字にすること
- CosmosDBのContainer作成時には、パーティションキーを設定すること
```

### ユーザメッセージ

また、システムメッセージを使いまわして、ユーザメッセージで各々の要件を追加するシーンもあると思うので、以下のようなユーザメッセージにして推論してもらいました。
```text
構成図です。
# 追加要求
- StaticWebAppsのリージョン情報は、他リソースのリージョン設定とは別のパラメータ「locationSWA」としてパラメータファイルに記述してください。
```

### GPT4Vの推論結果

以下のように、GPT4Vが推論してくれました。英語になってますが、、、問題なさそうです。
システムメッセージに「日本語で。」と書いておけば、日本語で返してくれると思います。
※表記の関係上、「\```」を「\\```」に変換しています。


`parameters.json`:  
   
```json  
{  
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",  
  "contentVersion": "1.0.0.0",  
  "parameters": {  
    "location": {  
      "value": "JapanEast"  
    },  
    "locationSWA": {  
      "value": "eastasia"  
    }  
  }  
}  
```  
   

`staticWebApp.bicep`:  
```bicep
`staticWebApp.bicep`:  
```bicep  
param locationSWA string  
param staticWebAppName string  
   
resource staticWebApp 'Microsoft.Web/staticSites@2020-12-01' = {  
  name: staticWebAppName  
  location: locationSWA  
  // Additional properties and settings for Static Web App  
}  
```  
   
`functions.bicep`:  
```bicep  
param location string  
param functionsName string  
   
resource functions 'Microsoft.Web/sites@2020-12-01' = {  
  name: functionsName  
  location: location  
  kind: 'functionapp'  
  // Additional properties and settings for Functions  
}  
```  
   
`storageAccount.bicep`:  
```bicep  
param location string  
param storageAccountName string  
   
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {  
  name: take(storageAccountName, 24)  
  location: location  
  sku: {  
    name: 'Standard_LRS'  
  }  
  kind: 'StorageV2'  
  // Additional properties and settings for Storage Account  
}  
```  
   
`cosmosDb.bicep`:  
```bicep  
param location string  
param cosmosDbAccountName string  
param databaseName string  
param containerStatusName string  
param containerLogName string  
   
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2021-04-15' = {  
  name: cosmosDbAccountName  
  location: location  
  // Additional properties and settings for Cosmos DB Account  
}  
   
resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-04-15' = {  
  name: '${cosmosDbAccount.name}/${databaseName}'  
  properties: {  
    resource: {  
      id: databaseName  
    }  
    options: {}  
  }  
}  
   
resource containerStatus 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-04-15' = {  
  name: '${database.name}/${containerStatusName}'  
  properties: {  
    resource: {  
      id: containerStatusName  
      partitionKey: {  
        paths: ['/partitionKey']  
        kind: 'Hash'  
      }  
    }  
    options: {}  
  }  
}  
   
resource containerLog 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-04-15' = {  
  name: '${database.name}/${containerLogName}'  
  properties: {  
    resource: {  
      id: containerLogName  
      partitionKey: {  
        paths: ['/partitionKey']  
        kind: 'Hash'  
      }  
    }  
    options: {}  
  }  
}  
```  

`main.bicep`:  
```bicep  
param location string  
param locationSWA string  
   
var uniqueSuffix = uniqueString(resourceGroup().id)  
var staticWebAppName = 'shrkm-staticwebapp-${uniqueSuffix}'  
var functionsName = 'shrkm-functions-${uniqueSuffix}'  
var storageAccountName = 'shrkmstorage${uniqueSuffix}'  
var cosmosDbAccountName = 'shrkm-cosmosdb-${uniqueSuffix}'  
var databaseName = 'sample-db'  
var containerStatusName = 'status'  
var containerLogName = 'log'  
   
module staticWebAppModule 'staticWebApp.bicep' = {  
  name: 'staticWebAppDeployment'  
  params: {  
    locationSWA: locationSWA  
    staticWebAppName: staticWebAppName  
  }  
}  
   
module functionsModule 'functions.bicep' = {  
  name: 'functionsDeployment'  
  params: {  
    location: location  
    functionsName: functionsName  
  }  
}  
   
module storageAccountModule 'storageAccount.bicep' = {  
  name: 'storageAccountDeployment'  
  params: {  
    location: location  
    storageAccountName: storageAccountName  
  }  
}  
   
module cosmosDbModule 'cosmosDb.bicep' = {  
  name: 'cosmosDbDeployment'  
  params: {  
    location: location  
    cosmosDbAccountName: cosmosDbAccountName  
    databaseName: databaseName  
    containerStatusName: containerStatusName  
    containerLogName: containerLogName  
  }  
}
```


生成されたBicepコードを実際にファイルにして、VSCodeで開いてみます。
必要なファイルは、
- staticwebapp.bicep
- functions.bicep
- storageaccount.bicep
- cosmosdb.bicep
- main.bicep
の5つです。

BicepVisualizer拡張機能で可視化すると以下のようになります。
![](/images/bicep-from-archi-image-poweredbyopenai/2024-03-31-07-38-08.png)


デプロイして問題なく払い出せました。


# まとめ
GPT4Vを使って、Azure構成図からBicepコードを生成してみて、システムメッセージの工夫によって、Bicepコードを生成させて、手修正なしでデプロイできました。
実際には、各リソースのプロパティを要件に応じて追加する必要がありますが、構成図からBicepコードを生成するということができることがわかりました。
リソースの要件は、ユーザメッセージに記載しておくと推論時に考慮してくれると思います。

注意事項として、GPT4Vの学習データ期間によって、最新のリソースやプロパティが反映されていない可能性があるので、その点は注意が必要です。
この点を補うなら、GPT4Vで推論させたBicepコードに対して、RAGで取得した最新のリソース設定でGPT3/4などを使いレビュ＆修正させるなんて方法もありそうです。