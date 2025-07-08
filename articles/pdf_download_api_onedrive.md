---
title: ""
emoji: "🎃"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

https://learn.microsoft.com/ja-jp/onedrive/developer/rest-api/api/driveitem_get_content_format?view=odsp-graph-online

# Entra ID でアプリ登録する
「アプリの登録」画面から「新規登録」します。
![](/images/pdf_download_api_onedrive/2025-05-22-12-07-04.png)

アプリ登録し、テナントIDとクライアントIDを控えておきましょう。
e4ed36be-38d0-4ddd-9c85-0962719b3135
467e8a90-b2ae-4e72-b66d-4d3029486290
![](/images/pdf_download_api_onedrive/2025-05-22-10-42-30.png)

<!-- 作成したアプリの「証明書とシークレット」画面から「新しいクライアントシークレット」を作成します。
secret-onedrive-poc-0522
![](/images/pdf_download_api_onedrive/2025-05-22-10-43-50.png)

クライアントシークレットを追加します。表示されるシークレットの値を控えておきましょう。
6iz8Q~ZWNjWRmCypeMzzjKPu-M.6rf0pqfq0VafI
![](/images/pdf_download_api_onedrive/2025-05-22-10-45-14.png) -->

# コードの実装

```python
import requests
from msal import PublicClientApplication

# アプリ登録の情報を設定
client_id = "YOUR_CLIENT_ID"
tenant_id = "YOUR_TENANT_ID"
scope = ["https://graph.microsoft.com/.default"]

# Microsoft Graphのエンドポイント
endpoint = "https://graph.microsoft.com/v1.0/me/drive/items/{item-id}/content"

# MSALを使った認証
def get_access_token():
    app = PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_id}")
    accounts = app.get_accounts()
    if accounts:
        # 既存のアカウントを使用する
        result = app.acquire_token_silent(scope, account=accounts[0])
    else:
        # アカウントがない場合は認証フローを開始
        result = app.acquire_token_interactive(scope)

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Authentication failed!")

# ファイルをダウンロードする関数
def download_file(file_id, download_format):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": download_format  # 例: "application/pdf"
    }

    response = requests.get(endpoint.format(item-id=file_id), headers=headers)
    if response.status_code == 200:
        with open("downloaded_file", "wb") as file:
            file.write(response.content)
        print("ファイルが正常にダウンロードされました。")
    else:
        print(f"エラーが発生しました: {response.status_code}")
        print(response.text)

# 使用例
download_file("YOUR_FILE_ID", "application/pdf")
```