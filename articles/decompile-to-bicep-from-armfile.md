---
title: "デプロイ済みAzureリソースのARMテンプレートをBicepコードに変換してIaC化したい！"
emoji: "📜"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "Bicep", "ARM"]
published: true
---

# はじめに
PoCのような形でAzure利用を開始し、サービスを手動で払い出していくといつの間にかリソースが増えていることがあります。
その構成を丸々コピーして複製したい場合には、IaC化されていないため、また一から手動でリソースを作成する羽目になります。
そのようなシーンを想定し、この記事では以下のような内容を解説します。
1. 既存のAzureリソースのARMテンプレートを取得
2. ARMテンプレートをBicepコードに変換
3. Bicepコードを修正
4. Bicepリンターでチェック
5. 修正したBicepコードをもとに新しいリソースを複製

# 環境構築
Bicepを利用するには以下の環境が必要です。今回はVSCodeを利用します。[公式ページはこちら](https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/install)
- VSCodeの拡張機能「Bicep」をインストール
    ![VSCodeの拡張機能「Bicep」](/images/decompile-to-bicep-from-armfile/2024-02-04-18-59-25.png)
- Azure CLIをインストール
    [AzureCLIインストール](https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/bicep/install#azure-cli)
  - Azure CLIをインストールしたら、以下のコマンドでBicepをインストールします。
    ```bash
    az bicep install
    ```
    ![Bicepインストール](/images/decompile-to-bicep-from-armfile/2024-02-04-19-10-57.png)
  - バージョンを確認します。
    ```bash
    az bicep -version
    ```
    ![Bicepバージョン確認](/images/decompile-to-bicep-from-armfile/2024-02-04-19-11-30.png)

# 実際に既存リソースからBicepコードへの変換を試します。

## 対象にするリソース

今回の記事では以下のリソースをBicep化してみます。WebアプリケーションをAzure上で構築するときにはよく利用するリソースだと思います。
![変換するリソース](/images/decompile-to-bicep-from-armfile/2024-02-04-22-12-08.png)
- StorageAccount（Functionが使う）
- AppServicePlan（FunctionとWebAppが使う）
- Functions
- WebApp

リソースごとに以下1-5を実施します。
1. 既存のAzureリソースのARMテンプレートを取得
2. ARMテンプレートをBicepコードに変換
3. Bicepコードを修正
4. Bicepリンターでチェック
5. 修正したBicepコードをもとに新しいリソースを複製

# ARMテンプレートを取得しBicepコードに変換し、修正する

## StorageAccount

### ①リソースのARMテンプレートを取得
AzureポータルからリソースのARMテンプレートを取得します。
![StorageAccountのARMテンプレート](/images/decompile-to-bicep-from-armfile/2024-02-04-19-40-16.png)

### ②ARMテンプレートをBicepコードに変換
- bicepコマンドでdecompileします。
```bash
az bicep decompile -file main.json
```

### ③Bicepコードを修正

以下6件のワーニングが発生しました。
![decompile storageAccount](/images/decompile-to-bicep-from-armfile/2024-02-04-19-46-13.png)

1. 1つ目のWarning
    locationがハードコーディングされているために発生したWarningです。
    ```
    Warning no-hardcoded-location: A resource location should not use a hard-coded string or variable value. Please use a parameter value, an expression, or the string 'global'. Found: 'japaneast' [https://aka.ms/bicep/linter/no-hardcoded-location]
    ```
    確かにこのようにハードコーディングされていますね。
    ```bicep
    param storageAccounts_st4func_name string = 'st4func'

    resource storageAccounts_st4func_name_resource 'Microsoft.Storage/storageAccounts@2023-01-01' = {
        name: storageAccounts_st4func_name
        location: 'japaneast'
    ```
    パラメータ化します。
    ```bicep
    param storageAccounts_st4func_name string = 'st4func'
    param storageAccounts_location string = 'japaneast'

    resource storageAccounts_st4func_name_resource 'Microsoft.Storage/storageAccounts@2023-01-01' = {
        name: storageAccounts_st4func_name
        location: storageAccounts_location
    ```

2. 2つ目のWarning
    tierが読み取り専用パラーメータのため、発生したWarningです。
    ```
    Warning BCP073: The property "tier" is read-only. Expressions cannot be assigned to read-only properties. If this is an inaccuracy in the documentation, please report it to the Bicep Team. [https://aka.ms/bicep-type-issues]
    ```
    tierが指定されているため、
    ```bicep
    sku: {
        name: 'Standard_LRS'
        tier: 'Standard'
    }
    ```
    tierの指定を削除します。
    ```bicep
    sku: {
        name: 'Standard_LRS'
    }
    ```

3. 3つ目と4つ目のWarning
    skuが読み取り専用パラーメータのため、発生したWarningです。
    ```
    Warning BCP073: The property "sku" is read-only. Expressions cannot be assigned to read-only properties. If this is an inaccuracy in the documentation, please report it to the Bicep Team. [https://aka.ms/bicep-type-issues]
    ```
    skuが指定されているため、この設定を削除します。
    ```bicep
    sku: {
        name: 'Standard_LRS'
        tier: 'Standard'
    }
    ```

4. 5つ目と6つ目のWarning
    
    ```
    Warning no-unnecessary-dependson: Remove unnecessary dependsOn entry 'storageAccounts_st4func001_name_resource'. [https://aka.ms/bicep/linter/no-unnecessary-dependson]
    ```
    dependsOnが指定されているため、この設定を削除します。
    ```bicep
    resource storageAccounts_st4func_name_default_azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
        parent: storageAccounts_st4func_name_default
        name: 'azure-webjobs-hosts'
        properties: {
            immutableStorageWithVersioning: {
                enabled: false
            }
            defaultEncryptionScope: '$account-encryption-key'
            denyEncryptionScopeOverride: false
            publicAccess: 'None'
        }
        dependsOn: [
            storageAccounts_st4func_name_resource
        ]
    }
    ```
    このdependsOnを削除します。
    ```bicep
    resource storageAccounts_st4func_name_default_azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
        parent: storageAccounts_st4func_name_default
        name: 'azure-webjobs-hosts'
        properties: {
            immutableStorageWithVersioning: {
                enabled: false
            }
            defaultEncryptionScope: '$account-encryption-key'
            denyEncryptionScopeOverride: false
            publicAccess: 'None'
        }
    }
    ```

:::details 最終的なBicepコードはこちらのようになります。
```bicep
param storageAccounts_st4func_name string = 'st4func'
param storageAccounts_location string = 'japaneast'

resource storageAccounts_st4func_name_resource 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccounts_st4func_name
  location: storageAccounts_location
  tags: {
    cost: ''
  }
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    dnsEndpointType: 'Standard'
    defaultToOAuthAuthentication: false
    publicNetworkAccess: 'Enabled'
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: true
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        table: {
          keyType: 'Account'
          enabled: true
        }
        queue: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

resource storageAccounts_st4func_name_default 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccounts_st4func_name_resource
  name: 'default'
  properties: {
    changeFeed: {
      enabled: false
    }
    restorePolicy: {
      enabled: false
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      allowPermanentDelete: false
      enabled: true
      days: 7
    }
    isVersioningEnabled: false
  }
}

resource Microsoft_Storage_storageAccounts_fileServices_storageAccounts_st4func_name_default 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccounts_st4func_name_resource
  name: 'default'
  properties: {
    protocolSettings: {
      smb: {}
    }
    cors: {
      corsRules: []
    }
    shareDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource Microsoft_Storage_storageAccounts_queueServices_storageAccounts_st4func_name_default 'Microsoft.Storage/storageAccounts/queueServices@2023-01-01' = {
  parent: storageAccounts_st4func_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource Microsoft_Storage_storageAccounts_tableServices_storageAccounts_st4func_name_default 'Microsoft.Storage/storageAccounts/tableServices@2023-01-01' = {
  parent: storageAccounts_st4func_name_resource
  name: 'default'
  properties: {
    cors: {
      corsRules: []
    }
  }
}

resource storageAccounts_st4func_name_default_azure_webjobs_hosts 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccounts_st4func_name_default
  name: 'azure-webjobs-hosts'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
}

resource storageAccounts_st4func_name_default_azure_webjobs_secrets 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: storageAccounts_st4func_name_default
  name: 'azure-webjobs-secrets'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
}
```
:::

### ④Bicepリンターでチェック
修正したら、Bicepリンターで、Bicepファイルに構文エラーとベストプラクティス違反がないかチェックします。
※VSCodeでBicepExtentionをインストールしておくと、bicepファイルを開いておけ自動でlintチェックされ違反コードが表示されます。ここでは念のため明示的にコマンドでチェックします。
```bash
az bicep lint -file .\template.bicep
```
![bicep lint storageAccount](/images/decompile-to-bicep-from-armfile/2024-02-04-20-29-46.png)

### ⑤修正したBicepコードをもとに新しいリソースを複製

Parameterファイルを作成します。パラメータは「storageAccounts_st4func_name」と「storageAccounts_location」が必要です。
```bicep
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "storageAccounts_st4func_name": {
            "value": "st4funcnew"
        },
        "storageAccounts_location": {
            "value": "japaneast"
        }
    }
}
```

VSCodeでデプロイします。
1. Bicep ファイル名を右クリック
    ![right-click bicep file](/images/decompile-to-bicep-from-armfile/2024-02-04-20-33-51.png)
2. デプロイ名を入力
    ![デプロイ名を入力](/images/decompile-to-bicep-from-armfile/2024-02-04-20-42-30.png)
3. Azure にサインインしてサブスクリプションを選択　※サブスクが一つしかなければ選択がスキップされます。
4. リソース グループを選択または作成
    ![リソース グループを作成](/images/decompile-to-bicep-from-armfile/2024-02-04-20-40-33.png)
5. パラメーター ファイルを選択。※選択しない場合はパラメーター値を入力
    ![パラメーター ファイルを選択](/images/decompile-to-bicep-from-armfile/2024-02-04-20-41-09.png)
6. VSCodeのOutputコンソールに「Deployment succeeded」と表示されればデプロイ完了です。
    ![Deployment succeeded](/images/decompile-to-bicep-from-armfile/2024-02-04-20-44-59.png)
7. リンクのAzurePortalにアクセスすると、リソースが作成されたことがわかります。
    ![CreatedResource AzurePortal](/images/decompile-to-bicep-from-armfile/2024-02-04-20-46-56.png)

## AppServicePlan
AppServicePlanも、StorageAccountと同じようにARMテンプレートを取得し、Bicepコードに変換します。

### ①リソースのARMテンプレートを取得
AzureポータルからリソースのARMテンプレートを取得します。
![AppServicePlan ARMテンプレート](/images/decompile-to-bicep-from-armfile/2024-02-04-22-19-27.png)

### ②ARMテンプレートをBicepコードに変換
- bicepコマンドでdecompileします。
```bash
az bicep decompile -file .\template.json
```

### ③Bicepコードを修正
bicepファイルが作成されました。Warningが1件だけあります。
![AppServicePlan BicepDecompile](/images/decompile-to-bicep-from-armfile/2024-02-04-22-21-40.png)

- locationパラメータがハードコーディングされている
    ```
    Warning no-hardcoded-location: A resource location should not use a hard-coded string or variable value. Please use a parameter value, an expression, or the string 'global'. Found: 'Japan East' [https://aka.ms/bicep/linter/no-hardcoded-location]
    ```
    locationをパラメータ化します。
    ```bicep
    param serverfarms_ASP_001_name string = 'ASP-001'
    param API_location string = 'japaneast'

    resource serverfarms_ASP_001_name_resource 'Microsoft.Web/serverfarms@2023-01-01' = {
        name: serverfarms_ASP_001_name
        location: API_location
    ```

:::details 最終的なAppServicePlanのBicepコードはこちらのようになります。
```bicep
param serverfarms_ASP_001_name string = 'ASP-001'
param API_location string = 'japaneast'

resource serverfarms_ASP_001_name_resource 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: serverfarms_ASP_001_name
  location: API_location
  tags: {
    cost: ''
  }
  sku: {
    name: 'P3v3'
    tier: 'PremiumV3'
    size: 'P3v3'
    family: 'Pv3'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 1
    isSpot: false
    reserved: true
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
  }
}
```
:::

### ④Bicepリンターでチェック
修正したら、Bicepリンターで、Bicepファイルに構文エラーとベストプラクティス違反がないかチェックします。
```bash
az bicep lint -file .\template.bicep
```
![bicep lint appservicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-29-53.png)

### ⑤修正したBicepコードをもとに新しいリソースを複製
Parameterファイルを作成します。パラメータは「serverfarms_ASP_001_name」と「API_location」が必要です。
```bicep
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "serverfarms_ASP_001_names": {
            "value": "ASP-new"
        },
        "API_location": {
            "value": "japaneast"
        }
    }
}
```

VSCodeでデプロイします。
1. Bicep ファイル名を右クリック
    ![right-click bicepfile AppServicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-33-48.png)
2. デプロイ名を入力
    ![deployname AppServicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-35-38.png)
3. リソースグループを入力
    ![リソースグループ入力 AppServicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-36-14.png)
4. パラメーターファイルを選択
    ![パラメーターファイルを選択 AppServicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-36-48.png)
5. VSCodeのOutputコンソールに「Deployment succeeded」と表示されればデプロイ完了です。
    ![DeploySucceeded AppServicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-38-52.png)
6. リンクのAzurePortalにアクセスすると、リソースが作成されたことがわかります。
    ![deployed resource AppServicePlan](/images/decompile-to-bicep-from-armfile/2024-02-04-22-40-35.png)
    AppServicePlanのリソースIDを確認します。後ほどFunctionやAppServiceのparameterファイルで使用します。
    ![AppServicePlanのリソースID](/images/decompile-to-bicep-from-armfile/2024-02-04-22-44-12.png)


## Functions
Functionも、StorageAccountと同じようにARMテンプレートを取得し、Bicepコードに変換します。

### ①リソースのARMテンプレートを取得
AzureポータルからリソースのARMテンプレートを取得します。
![FunctionのARMテンプレート](/images/decompile-to-bicep-from-armfile/2024-02-04-21-51-57.png)

### ②ARMテンプレートをBicepコードに変換
- bicepコマンドでdecompileします。
```bash
az bicep decompile -file .\template.json
```

### ③Bicepコードを修正
大量のWarningが発生しました。表示されている以外にもWarningがあります。。。一つ一つ修正していきましょう。
![Function Warning](/images/decompile-to-bicep-from-armfile/2024-02-04-21-54-53.png)

- locationをパラメータ化
    Warningの内容は以下です。
    ```
    Warning no-hardcoded-location: A resource location should not use a hard-coded string or variable value. Please use a parameter value, an expression, or the string 'global'. Found: 'Japan East' [https://aka.ms/bicep/linter/no-hardcoded-location]
    ```
    locationをパラメータ化します。
    ```bicep
    param func_location string = 'japaneast'

    resource sites_func_001_name_resource 'Microsoft.Web/sites@2023-01-01' = {
        name: sites_func_001_name
        location: func_location
    ```

- 定義にlocationパラメータとtagsパラメータが不要なため削除
    Warningの内容は以下です。
    ```
    Warning BCP187: The property "location" does not exist in the resource or type definition, although it might still be valid. If this is an inaccuracy in the documentation, please report it to the Bicep Team. [https://aka.ms/bicep-type-issues]
    ```
    locationとtagパラメータを削除します。

- リソースタイプ「"Microsoft.Web/sites/snapshots@2015-08-01"」を削除
    ```bicep
    Warning BCP081: Resource type "Microsoft.Web/sites/snapshots@2015-08-01" does not have types available.
    ```
    このリソースタイプは削除します。

Warningではありませんが、以下のような、既存のリソースのデプロイログも削除します。
```bicep
resource sites_func_001_name_05cf8410_7697_420a_895b_460fbde5d7f8 'Microsoft.Web/sites/deployments@2023-01-01' = {
  parent: sites_func_001_name_resource
  name: '05cf8410-7697-420a-895b-460fbde5d7f8'
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'ms-azuretools-vscode'
    deployer: 'ms-azuretools-vscode'
    message: 'Created via a push deployment'
    start_time: '2024-01-31T12:10:04.3612217Z'
    end_time: '2024-01-31T12:14:28.4116151Z'
    active: false
  }
}
```

同じように、既存のリソースのトリガー情報も削除します。
```bicep
resource sites_func_001_name_http_trigger_test 'Microsoft.Web/sites/functions@2023-01-01' = {
  parent: sites_func_001_name_resource
  name: 'http_trigger_test'
  properties: {
    script_href: 'https://func-001.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://func-001.azurewebsites.net/admin/vfs/home/data/Functions/sampledata/http_trigger_test.dat'
    href: 'https://func-001.azurewebsites.net/admin/functions/http_trigger_test'
    config: {}
    invoke_url_template: 'https://func-001.azurewebsites.net/api/http_trigger_test'
    language: 'python'
    isDisabled: false
  }
}
```

:::details 最終的なFunctionのBicepコードはこちらのようになります。
```bicep
param sites_func_001_name string = 'func-001'
param serverfarms_ASP_func_externalid string = '/subscriptions/{サブスクリプションID}/resourceGroups/rg-dev-eastus/providers/Microsoft.Web/serverfarms/ASP-001'
param func_location string = 'japaneast'

resource sites_func_001_name_resource 'Microsoft.Web/sites@2023-01-01' = {
  name: sites_func_001_name
  location: func_location
  kind: 'functionapp,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${sites_func_001_name}.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${sites_func_001_name}.scm.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: serverfarms_ASP_func_externalid
    reserved: true
    isXenon: false
    hyperV: false
    vnetRouteAllEnabled: false
    vnetImagePullEnabled: false
    vnetContentShareEnabled: false
    siteConfig: {
      numberOfWorkers: 1
      linuxFxVersion: 'PYTHON|3.10'
      acrUseManagedIdentityCreds: false
      alwaysOn: true
      http20Enabled: false
      functionAppScaleLimit: 0
      minimumElasticInstanceCount: 0
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    customDomainVerificationId: '6577131C27CD16A213D39EC5E4A2573F242595330E6F4FB08D64B3A8772F65A4'
    containerSize: 1536
    dailyMemoryTimeQuota: 0
    httpsOnly: true
    redundancyMode: 'None'
    publicNetworkAccess: 'Enabled'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
  }
}
```
:::

### ④Bicepリンターでチェック
修正したら、Bicepリンターで、Bicepファイルに構文エラーとベストプラクティス違反がないかチェックします。
```bash
az bicep lint -file .\template.bicep
```
![④Bicepリンターでチェック Function](/images/decompile-to-bicep-from-armfile/2024-02-06-22-41-33.png)

### ⑤修正したBicepコードをもとに新しいリソースを複製
Parameterファイルを作成します。パラメータは「sites_func_001_name」と「serverfarms_ASP_func_externalid」と「func_location」が必要です。
```bicep
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "sites_func_001_name": {
            "value": "func-new"
        },
        "serverfarms_ASP_func_externalid": {
            "value": "/subscriptions/{サブスクリプションID}/resourceGroups/rg-app-new/providers/Microsoft.Web/serverfarms/ASP-new"
        },
        "func_location": {
            "value": "japaneast"
        }
    }
}
```

VSCodeでデプロイします。
1. Bicep ファイル名を右クリック
    ![Deploy new function](/images/decompile-to-bicep-from-armfile/2024-02-06-22-56-44.png)
2. デプロイ名を入力
    ![デプロイ名を入力 func-new](/images/decompile-to-bicep-from-armfile/2024-02-06-23-00-37.png)
3. リソースグループを選択
    ![リソースグループを選択 func-new](/images/decompile-to-bicep-from-armfile/2024-02-06-23-01-10.png)
4. パラメータファイルを選択
    ![パラメータファイルを選択 func-new](/images/decompile-to-bicep-from-armfile/2024-02-06-23-02-45.png)
5. VSCodeのOutputコンソールに「Deployment succeeded」と表示されればデプロイ完了です。
    ![デプロイ完了 func-new](/images/decompile-to-bicep-from-armfile/2024-02-06-23-05-07.png)
6. リンクのAzurePortalにアクセスすると、リソースが作成されたことがわかります。
    ![作成されたFunctionリソース](/images/decompile-to-bicep-from-armfile/2024-02-06-23-06-39.png)

## WebApp

### ①リソースのARMテンプレートを取得
AzureポータルからリソースのARMテンプレートを取得します。
![①リソースのARMテンプレートを取得 WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-22-51-30.png)

### ②ARMテンプレートをBicepコードに変換
- bicepコマンドでdecompileします。
```bash
az bicep decompile -file .\template.json
```

### ③Bicepコードを修正
Functionと同じように、大量のWarningが発生しました。同じように修正していきましょう。

- locationをパラメータ化
    Warningの内容は以下です。
    ```
    Warning no-hardcoded-location: A resource location should not use a hard-coded string or variable value. Please use a parameter value, an expression, or the string 'global'. Found: 'Japan East' [https://aka.ms/bicep/linter/no-hardcoded-location]
    ```
    locationを以下のようにパラメータ化します。
    ```bicep
    param sites_func_001_name string = 'func-001'
    param serverfarms_ASP_func_externalid string = 'ASPのリソースID'
    param func_location string = 'japaneast'

    resource sites_func_001_name_resource 'Microsoft.Web/sites@2023-01-01' = {
        name: sites_func_001_name
        location: func_location
    ```
- 定義にlocationパラメータとtagsパラメータが不要なため削除
    Warningの内容は以下です。
    ```
    Warning BCP187: The property "location" does not exist in the resource or type definition, although it might still be valid. If this is an inaccuracy in the documentation, please report it to the Bicep Team. [https://aka.ms/bicep-type-issues]
    ```
    locationとtagパラメータを削除します。
- "Microsoft.Web/sites/snapshots@2015-08-01"のリソースタイプを削除
    ```bicep
    Warning BCP081: Resource type "Microsoft.Web/sites/snapshots@2015-08-01" does not have types available.
    ```
    このリソースタイプは削除します。

以下のような、既存のリソースのデプロイログも削除します。
```bicep
resource sites_web_001_name_103493bd_8dc0_428e_9ff0_9fb74ad4aaac 'Microsoft.Web/sites/deployments@2023-01-01' = {
  parent: sites_web_001_name_resource
  name: '103493bd-8dc0-428e-9ff0-9fb74ad4aaac'
  location: webapp_location
  properties: {
    status: 4
    author_email: 'N/A'
    author: 'ms-azuretools-vscode'
    deployer: 'ms-azuretools-vscode'
    message: 'Created via a push deployment'
    start_time: '2024-01-31T05:04:06.4846286Z'
    end_time: '2024-01-31T05:05:17.271309Z'
    active: false
  }
}
```

:::details 最終的なWebAppのBicepコードはこちらのようになります。
```bicep
param sites_web_001_name string = 'web-001'
param serverfarms_ASP_externalid string = '/subscriptions/{サブスクリプションID}/resourceGroups/rg-dev-eastus/providers/Microsoft.Web/serverfarms/ASP-001'
param webapp_location string = 'japaneast'

resource sites_web_001_name_resource 'Microsoft.Web/sites@2023-01-01' = {
  name: sites_web_001_name
  location: webapp_location
  kind: 'app,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${sites_web_001_name}.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${sites_web_001_name}.scm.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: serverfarms_ASP_externalid
    reserved: true
    isXenon: false
    hyperV: false
    vnetRouteAllEnabled: false
    vnetImagePullEnabled: false
    vnetContentShareEnabled: false
    siteConfig: {
      numberOfWorkers: 1
      linuxFxVersion: 'PYTHON|3.10'
      acrUseManagedIdentityCreds: false
      alwaysOn: true
      http20Enabled: false
      functionAppScaleLimit: 0
      minimumElasticInstanceCount: 0
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    customDomainVerificationId: '6577131C27CD16A213D39EC5E4A2573F242595330E6F4FB08D64B3A8772F65A4'
    containerSize: 0
    dailyMemoryTimeQuota: 0
    httpsOnly: true
    redundancyMode: 'None'
    publicNetworkAccess: 'Enabled'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
  }
}

resource sites_web_001_name_ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2023-01-01' = {
  parent: sites_web_001_name_resource
  name: 'ftp'
  properties: {
    allow: true
  }
}

resource sites_web_001_name_scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2023-01-01' = {
  parent: sites_web_001_name_resource
  name: 'scm'
  properties: {
    allow: true
  }
}

resource sites_web_001_name_web 'Microsoft.Web/sites/config@2023-01-01' = {
  parent: sites_web_001_name_resource
  name: 'web'
  properties: {
    numberOfWorkers: 1
    defaultDocuments: [
      'Default.htm'
      'Default.html'
      'Default.asp'
      'index.htm'
      'index.html'
      'iisstart.htm'
      'default.aspx'
      'index.php'
      'hostingstart.html'
    ]
    netFrameworkVersion: 'v4.0'
    linuxFxVersion: 'PYTHON|3.10'
    requestTracingEnabled: false
    remoteDebuggingEnabled: false
    remoteDebuggingVersion: 'VS2019'
    httpLoggingEnabled: false
    acrUseManagedIdentityCreds: false
    logsDirectorySizeLimit: 35
    detailedErrorLoggingEnabled: false
    publishingUsername: '$web-001'
    scmType: 'None'
    use32BitWorkerProcess: true
    webSocketsEnabled: false
    alwaysOn: true
    appCommandLine: ''
    managedPipelineMode: 'Integrated'
    virtualApplications: [
      {
        virtualPath: '/'
        physicalPath: 'site\\wwwroot'
        preloadEnabled: true
      }
    ]
    loadBalancing: 'LeastRequests'
    experiments: {
      rampUpRules: []
    }
    autoHealEnabled: false
    vnetRouteAllEnabled: false
    vnetPrivatePortsCount: 0
    publicNetworkAccess: 'Enabled'
    localMySqlEnabled: false
    ipSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictionsUseMain: false
    http20Enabled: false
    minTlsVersion: '1.2'
    scmMinTlsVersion: '1.2'
    ftpsState: 'FtpsOnly'
    preWarmedInstanceCount: 0
    elasticWebAppScaleLimit: 0
    functionsRuntimeScaleMonitoringEnabled: false
    minimumElasticInstanceCount: 0
    azureStorageAccounts: {}
  }
}
```
:::

### ④Bicepリンターでチェック
修正したら、Bicepリンターで、Bicepファイルに構文エラーとベストプラクティス違反がないかチェックします。
```bash
az bicep lint -file .\template.bicep
```
![④Bicepリンターでチェック WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-23-23-49.png)

### ⑤修正したBicepコードをもとに新しいリソースを複製
Parameterファイルを作成します。パラメータは「sites_web_001_name」と「serverfarms_ASP_externalid」と「webapp_location」が必要です。
```bicep
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "sites_web_001_name": {
            "value": "webapp-new"
        },
        "serverfarms_ASP_externalid": {
            "value": "/subscriptions/{サブスクリプションID}/resourceGroups/rg-app-new/providers/Microsoft.Web/serverfarms/ASP-new"
        },
        "webapp_location": {
            "value": "japaneast"
        }
    }
}
```

VSCodeでデプロイします。
1. Bicep ファイル名を右クリック
    ![Deploy new WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-23-26-08.png)
2. デプロイ名を入力
    ![デプロイ名を入力 WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-23-26-37.png)
3. リソースグループを選択
    ![リソースグループを選択 WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-23-27-03.png)
4. パラメータファイルを選択
    ![パラメータファイルを選択 WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-23-27-38.png)
5. VSCodeのOutputコンソールに「Deployment succeeded」と表示されればデプロイ完了です。
    ![デプロイ完了 WebApp](/images/decompile-to-bicep-from-armfile/2024-02-06-23-33-04.png)
6. リンクのAzurePortalにアクセスすると、リソースが作成されたことがわかります。
    ![作成されたWebAppリソース](/images/decompile-to-bicep-from-armfile/2024-02-06-23-34-18.png)

# まとめ
以上で、既存のAzureリソースをARMテンプレートからBicepに変換しIaC化し、既存リソースのワンセットを新規でデプロイすることができました。
今回はシンプルにBicepコードに変換して、リソースごと分かれたBicepファイルをそれぞれ別々にデプロイしました。そのため、複数のリソースを払い出す際には、それぞれのリソースの依存関係を考慮してデプロイする必要があります。
リソースごとのBicepファイルを参照したmain.bicepファイルを定義することで、複数のリソースを依存関係を考慮してまとめてデプロイできるようです。
次は、リソースごとにBicepファイルをもとに、一連のリソースを一気にデプロイする方法を試したいと思います。

また、実際にはリソース作成だけではなく環境変数も設定したくなります。CICDの一貫として、ソースコードデプロイと環境変数の設定を一気に行う方法もいずれ検証しようと思います。