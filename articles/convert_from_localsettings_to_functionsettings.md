---
title: "local.settings.jsonをAzureFunctionsやWebAppsの構成設定Jsonに変換したい！"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "Functions", "WebApps", "Python"]
published: true
---

# 何をしたいか
AzureFunctionで動作するPythonプロジェクトをローカル開発する場合に用いるlocal.settings.jsonを、AzureFunctionsやWebAppsのアプリケーション設定のJsonに変換します。

# なぜしたいか

AzureFunctionで動作するPythonプロジェクトをローカル開発する場合、local.settings.jsonに環境変数を記述します。

以下は、アプリケーションが利用する独自の環境変数「ENVIRONMENT_SETTING_1」と「ENVIRONMENT_SETTING_2」をlocal.settings.jsonに記述した例です。
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "ENVIRONMENT_SETTING_1": "環境変数1",
    "ENVIRONMENT_SETTING_2": "環境変数2",
  }
}
```

このlocal.settings.jsonの構造のまま、FunctionやWebAppsの環境変数設定に設定できればいいのですが、AzureFunctionsやWebAppsのアプリケーション設定のJsonは、local.settings.jsonとは異なる構造になっています。
```json
[
  {
    "name": "FUNCTIONS_WORKER_RUNTIME",
    "value": "python",
    "slotSetting": false
  },
  {
    "name": "AzureWebJonsFeatureFlags",
    "value": "EnableWorkerIndexing",
    "slotSetting": false
  }
  {
    "name": "ENVIRONMENT_SETTING_1",
    "value": "環境変数1",
    "slotSetting": false
  },
  {
    "name": "ENVIRONMENT_SETTING_2",
    "value": "環境変数2",
    "slotSetting": false
  }
]
```

FunctionやWebAppsのアプリケーション設定は以下から確認します。
![Function/WebAppsのアプリケーション設定](/images/convert_from_localsettings_to_functionsettings/2024-03-05-21-28-58.png)

:::message alert
アプリケーションが大きくなると環境変数が増えていきます。デプロイ時に、開発時に追加した環境変数をアプリケーション設定にも追加しますが、手作業で変換するのは面倒ですし、ミスも発生しやすいです。
:::

# 変換するツール
local.settings.jsonをAzureFunctionsやWebAppsのアプリケーション設定のJsonに変換するPythonコードです。

```python
import json

# 1つ目のJSONファイルを読み込む
with open('local.settings.json', 'r') as f:
        data = json.load(f)

# "Values" キーの下のデータを新しい形式に変換する
new_data = [{"name": k, "value": v, "slotSetting": False} for k, v in data["Values"].items()]

# 新しいデータを2つ目のJSONファイルに書き込む
with open('created_function_settings.json', 'w') as f:
        json.dump(new_data, f, indent=4)
```

実行するディレクトリにlocal.settings.jsonを配置し、上記のPythonコードを実行すると、created_function_settings.jsonが生成されます。
このjsonファイルをAzureFunctionsやWebAppsのアプリケーション設定の高度な編集画面で追加することで、抜け漏れやミスなく環境変数を設定できます。

DevOpsの観点で、デプロイパイプラインに組み込むことで、環境変数の設定を自動化することもできます。