---
title: "StreamlitアプリをAzureのAppServiceで動かす"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "OpenAI", "AppService", "Streamlit", "Python"]
published: true
---

# StreamlitアプリをAzureのAppServiceで動かす

## 紹介すること／紹介しないこと
- こちらの記事では、[OpenAIを簡単に検証するためにStreamlitを使う](https://zenn.dev/nomhiro/articles/streamlit-use-openai)方法を紹介しました。紹介したStreamlitアプリをAzureのAppServiceにデプロイしWebアプリとして公開する方法を紹介します。

## AzureAppSericeとは
- AzureAppSericeとは、Azure上でWebアプリケーションをホストするためのサービスです。
- AzureAppSericeは、AzureのPaaSサービスの一つで、サーバーの管理やOSの管理などをAzureが行ってくれるため、Webアプリケーションの開発に集中することができます。

## AppServiceの作成とデプロイ手順

### AppServiceリソースの作成
1. AzureポータルからAppServiceを検索し新規作成します。
2. AppServiceの「基本」情報を入力します。
    ※Dockerコンテナで動作するように設定しています。
    :::message alert
    PrivateEndpointを利用する場合は、現状はPremiumプランが必要ですのでご注意ください。
    :::
    ![AppService基本](/images/deploy-streamlit-to-appservice/(/images/deploy-streamlit-to-appservice/2023-12-27-10-04-34.png).png)
3. その他のタブの設定は必要に応じて設定してください。
4. 「確認＋作成」をクリックします。

### Sreamlitアプリ起動のための設定
1. AppServiceの「構成」タブを開きます。
2. 「全般設定」の「スタートアップコマンド」に以下のコマンドを設定します。
    ```bash
    python -m streamlit run chat.py --server.port 8000 --server.address 0.0.0.0
    ```
    ![Streamlitスタートアップコマンド設定](/images/deploy-streamlit-to-appservice/2023-12-27-22-47-31.png)
Streamlitアプリを起動するためのスタートアップコマンドを設定します。
3. 「保存」をするとAppServiceが再起動し、Streamlitアプリが起動します。

### まとめ
AzureのAppServiceにStreamlitアプリをデプロイすることができました。
次は、StreamlitアプリをAzureのApplicationGatewayを利用してプライベートエンドポイントとして公開する方法を紹介します。