---
title: "ApplicationGatewayを介してAppService上のSteamlitアプリに接続する方法"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "ApplicationGateway", "Streamlit", "WebApp"]
published: true
---

# はじめに
以前の記事で、Streamlitを使って簡単なWebアプリを作成する方法を紹介しました。
https://zenn.dev/nomhiro/articles/streamlit-use-openai
また、Azure WebAppを使ってStreamlitのアプリを公開する方法も紹介しました。
https://zenn.dev/nomhiro/articles/deploy-streamlit-to-appservice

**この記事では、ApplicationGatewayを介してAppService上で稼働するStreamlitのアプリにアクセスする方法を紹介します。**
必要な設定は、Streamlit側の設定変更と、ApplicationGatewayの設定の2つです。

# そもそもApplicationGatewayを使うと何が嬉しいか
- ApplicationGatewayは、L7ロードバランサーなので、HTTP/HTTPSのレイヤーでのロードバランシングします。つまり、URLやホストヘッダーなどのHTTP/HTTPSの情報を元に、リクエストを振り分けることができます。
    - 例：**リクエストURLによる振り分け**
    `https://cost.example.com`と`https://peaple.example.com`の2つのアプリケーションがある場合、ApplicationGatewayを使って、`https://shrkmn.com`のURLをもとに、2つのアプリケーションにルーティングできます。
    ![リクエストURLによる振り分け](/images/streamlitapp-via-applicationgateway/2024-02-11-09-19-36.png)
    - 例：**複数のアプリケーションを1つのIPアドレスで公開**
    上記の図のように`https://cost.example.com`と`https://peaple.example.com`の2つのアプリケーションがある場合、ApplicationGatewayを使って、1つのIPアドレスで2つのアプリケーションを公開できます。
    - 例：**負荷分散**
    複数のサーバで同じアプリケーションを動かしている場合、ApplicationGatewayを使ってリクエストを複数のサーバに分散することができます。

※AzureLoadBalancerというL4ロードバランサーもありますが、こちらはTCP/UDPのレイヤーでのロードバランシングが可能です。

# 証明書を用意
ApplicationGatewayでHTTPSを使う場合、証明書が必要です。
https://learn.microsoft.com/ja-jp/entra/identity-platform/howto-create-self-signed-certificate#optional-export-your-public-certificate-with-its-private-key

certnameは必要に応じて変えてください。
```bash
$certname = "streamlitapp"
```
```bash
$cert = New-SelfSignedCertificate -Subject "CN=$certname" -CertStoreLocation "Cert:\CurrentUser\My" -KeyExportPolicy Exportable -KeySpec Signature -KeyLength 2048 -KeyAlgorithm RSA -HashAlgorithm SHA256
```
```bash
Export-Certificate -Cert $cert -FilePath "$certname.cer"
```

{myPassword}を変更してください。ApplicationGatewayのリスナー設定する際に、このパスワードが必要になります。
```bash
$mypwd = ConvertTo-SecureString -String "{myPassword}" -Force -AsPlainText
```
```bash
Export-PfxCertificate -Cert $cert -FilePath "C:\Users\admin\Desktop\$certname.pfx" -Password $mypwd
```
作成したpfxファイルはApplicationGatewayのリスナー設定する際に使用します。

# Steamlitの設定変更
**Steamlitでは、デフォルトでCORSが有効になっています。なにも設定しないと、ApplicationGatewayのFQDNからのリクエストを拒否してしまいます。**
そのため、`--server.enableCORS`、`--browser.serverPort`, `--browser.serverAddress`オプションを使って、ApplicationGatewayのFQDNからのリクエストを許可するように設定します。
```bash
python -m streamlit run chat.py --server.port 8000 --server.address 0.0.0.0 --server.enableCORS true --browser.serverPort 443 --browser.serverAddress {ApplicationGatewayのリスナーに設定するFQDN}
```
- `--server.enableCORS`:CORSを有効にするオプション
- `--browser.serverPort`:ApplicationGatewayのポートです。
- `--browser.serverAddress`:ApplicationGatewayのリスナーに設定するFQDNです。

AppServiceの「構成」-「全般設定」-「スタートアップコマンド」に設定します。
![AppServiceスタートアップコマンド](/images/streamlitapp-via-applicationgateway/2024-02-17-10-53-57.png)

# ApplicationGatewayの作成

ApplicationGatewayには、ApplicationGateway専用の仮想ネットワークサブネットが必要です。
https://learn.microsoft.com/ja-jp/azure/application-gateway/configuration-infrastructure
なので、まずはサブネットを作成します。
![ApplicationGateway作成](/images/streamlitapp-via-applicationgateway/2024-02-17-09-22-37.png)

ApplicationGatewayを作成します。
※ここでは検証目的のため、インスタンス数MAX2、可用性ゾーンはなしにしています。要件に応じて変更してください。
公式ページはこちらです。
https://learn.microsoft.com/ja-jp/azure/application-gateway/application-gateway-autoscaling-zone-redundant

![ApplicationGateway基本](/images/streamlitapp-via-applicationgateway/(/images/streamlitapp-via-applicationgateway/2024-02-17-09-53-26.png).png)

![ApplicationGatewayフロントエンド](/images/streamlitapp-via-applicationgateway/2024-02-17-09-54-39.png)

バックエンドはStreamlitアプリを公開しているAppServiceを指定します。
![ApplicationGatewayバックエンド](/images/streamlitapp-via-applicationgateway/2024-02-17-09-29-31.png)

リスナー設定で、事前に作成したpfxファイルとパスワードを指定します。
ここで設定するホスト名は、ApplicationGatewayを介してStreamlitアプリにアクセスするためのFQDNになります。
![ApplicationGateway構成-リスナー設定](/images/streamlitapp-via-applicationgateway/2024-02-17-10-40-25.png)
バックエンドターゲットも設定します。
![ApplicationGateway構成-バックエンドターゲット](/images/streamlitapp-via-applicationgateway/2024-02-17-09-48-27.png)
バックエンド設定は上記の画面から新規追加を押下し設定します。
![ApplicationGateway構成-バックエンド設定](/images/streamlitapp-via-applicationgateway/(/images/streamlitapp-via-applicationgateway/2024-02-17-09-56-25.png).png)

# 稼働確認
ApplicationGatewayのFQDNにアクセスして、Streamlitのアプリが表示されることを確認します。
```https://{リスナーに設定したFQDN}```
ApplicationGatewayを介して、アプリに接続できました。
![](/images/streamlitapp-via-applicationgateway/2024-02-17-10-51-03.png)