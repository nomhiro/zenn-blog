---
title: "AppServiceのデプロイスロットを使って運用環境とステージング環境を切り替える"
emoji: "👾"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "AppService", "WebApp"]
published: true
---

# はじめに
AppService WebAppsでアプリをリリースする場合、従来であれば運用環境とステージング環境を切り替えるために、別々のWebAppを用意していました。しかし、WebAppのデプロイスロットを使うことで、同じWebApp内で運用環境とステージング環境を切り替えることができます。この記事では、AppService WebAppsのデプロイスロットを使って、運用環境とステージング環境を切り替える方法を紹介します。

# 前提
- 実行している App Service プランのサービス レベルが Standard、Premium、または Isolated であること。
https://learn.microsoft.com/ja-jp/azure/app-service/deploy-staging-slots?tabs=portal

# 事前準備

## AppService WebAppの払い出し
まず、試すためのAppService WebAppを作成します。
![](/images/deployslot_appservice_appgw/2024-04-15-22-13-15.png)

この内容で作成します。
![](/images/deployslot_appservice_appgw/2024-04-15-22-12-20.png)


# アプリの動確 ※スロット利用なし
稼働確認のためのアプリでは、環境変数「ENVIRONMENT_NAME」の値を取得し、画面に表示します。

**環境変数「ENVIRONMENT_NAME」は、各スロット固有の設定とみなします。**
※実際のアプリでは、DBへの接続情報などが該当しますね。
  - 運用スロット：「Production」
  - Stagingスロット：「Staging」


アプリのソースコードはこちらです。　超簡易的な画面です。
```python
import os
import streamlit as st

st.title("Deployslotの稼働確認用画面")

st.subheader(f"この環境は \"{os.environ['ENVIRONMENT_NAME']}\" です。")
```

WebAppには以下の二つの設定をしました。
:::details StreamlitをWebAppで起動するために、スタートアップコマンドを設定
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```
![](/images/deployslot_appservice_appgw/2024-04-15-22-53-37.png)
:::

:::details WebAppの構成ページから環境変数を追加します。
- 「ENVIRONMENT_NAME」の値に「Production」と設定します。
- 「SCM_DO_BUILD_DURING_DEPLOYMENT」の値に「1」と設定します。
※デプロイ時に、requirements.txtがある場合に、pip installを実行するための設定です。
![](/images/deployslot_appservice_appgw/2024-04-15-22-45-02.png)
:::


#### デプロイして、アプリ画面を確認
環境変数「ENVIRONMENT_NAME」の値に「Production」と設定したので、画面にもその値が表示されています。
![](/images/deployslot_appservice_appgw/2024-04-15-22-42-23.png)


# デプロイスロットの作成と設定
ここからが本題です！

#### デプロイスロットの作成

まずはデプロイスロットを作成します。名前は「staging」とします。
![](/images/deployslot_appservice_appgw/2024-04-15-22-46-30.png)

デプロイスロットが作成されました。
![](/images/deployslot_appservice_appgw/2024-04-15-22-47-31.png)

#### アプリ構成のための設定
作成されたデプロイスロットをクリックし、stagingスロットに対してアプリ構成のための設定をします。
::: details スタートアップコマンド
```bash
python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
```
![](/images/deployslot_appservice_appgw/2024-04-15-22-53-05.png)
:::

::: details 環境変数
  - 「ENVIRONMENT_NAME」の値に「Staging」と設定します。
  - 「SCM_DO_BUILD_DURING_DEPLOYMENT」の値に「1」と設定します。
![](/images/deployslot_appservice_appgw/2024-04-15-22-52-21.png)
:::

# StaginsSlotへのデプロイ～スワップ　※期待通りに動作しません
コードは、6行目のsubheaderを追加しただけです。
```python
import os
import streamlit as st

st.title("Deployslotの稼働確認用画面")

st.subheader("Stagingスロットを設定しました。")
st.subheader(f"この環境は \"{os.environ['ENVIRONMENT_NAME']}\" です。")
```

WebAppにデプロイします。
![](/images/deployslot_appservice_appgw/2024-04-15-23-06-06.png)

![](/images/deployslot_appservice_appgw/2024-04-15-23-06-32.png)

※今回はVSCodeからの手動デプロイで動作確認しますが、実際の利用ではGitHubActionsを用いたCICDを使って自動化することが望ましいです。
:::message
間違った作業で運用スロットにデプロイすることを避けるために、デフォルトのデプロイ先をstageスロットに設定しておくとよいでしょう。
![](/images/deployslot_appservice_appgw/2024-04-15-23-40-28.png)
VSCodeごとの設定なので、個人ごとの設定に依存してしまいますが、、、はやりCICDで自動化するのが一番ですね。
:::

デプロイ後、StagingスロットのURLにアクセスします。
URLは、運用スロットのURLに「-staging」を追加したものです。
（例）https://deployslot-testapp-staging.azurewebsites.net/

問題なく、アプリの更新がStagingスロットに反映されています。
![](/images/deployslot_appservice_appgw/2024-04-15-23-10-00.png)

アプリの稼働確認ができたので、運用スロットとスワップします。
:::message alert
実はこれだけの手順では、環境変数の情報もスワップの対象となってしまい、やりたいことが実現できていません。その内容をこの後で説明します。
:::
ソースとターゲットのスロット名と、構成変更内容（今回だと環境変数のみ）を確認して、スワップします。
![](/images/deployslot_appservice_appgw/2024-04-15-23-25-02.png)



スワップが完了したあと、運用スロットのURLにアクセスします。
（例）https://deployslot-testapp.azurewebsites.net/
![](/images/deployslot_appservice_appgw/2024-04-15-23-29-50.png)

:::message alert
お気づきだと思いますが、運用スロットのURLにアクセスしたのに、アプリで表示される環境は「Staging」になってしまっています。
運用スロットの環境変数をみると、「ENVIRONMENT_NAME」の値が「Staging」になっていまっています。
![](/images/deployslot_appservice_appgw/2024-04-16-00-22-05.png)
何が起こったかというと、スワップでは環境変数の情報もスワップ対象となるので、Stagingスロットの環墋変数が運用スロットに反映されてしまったのです。
**運用スロットとStagingスロットで、環境変数を別々に設定するためには、各スロットの環境変数に「デプロイスロットの設定」にチェックを入れる必要があります。**
※MicrosoftLearnのサイトでこの設定について説明がありましたが、いまいちピンとこなかったので、実際に試してみることで理解が深まりました。
:::


# 期待通りのスワップ
ここからが、やりたいことを実現するために必要な追加設定です。

運用スロットの環境変数に対し、「デプロイスロットの設定」にチェックを入れます。
![](/images/deployslot_appservice_appgw/2024-04-15-23-32-15.png)

Stagingスロットの環境変数に対し、「デプロイスロットの設定」にチェックを入れます。
![](/images/deployslot_appservice_appgw/2024-04-15-23-33-18.png)

さて、もう一度スワップしてみます。
「デプロイスロットの設定」にチェックを入れたため、環境変数はスワップの対象外となります。
![](/images/deployslot_appservice_appgw/2024-04-16-00-08-26.png)

運用スロットのURLにアクセスします。
（例）https://deployslot-testapp.azurewebsites.net/
アプリはスワップされ、環境変数は運用スロットに設定されていた「Production」がそのまま引き継がれています。期待通りの結果です。
![](/images/deployslot_appservice_appgw/2024-04-16-00-13-29.png)


# まとめ
AppService WebAppsのデプロイスロットを使うことで、**運用環境とステージング環境を切り替える**ことができます。運用環境への影響を最小限に抑えながら、新しい機能のテストやバグの検証できるので非常に便利です。

また、スワップ後に不具合が発覚した場合でも、**切り戻しが簡単**です。再度運用スロットとStagingスロットをスワップするだけで、以前の状態に戻せるからです。


#### 参考にさせていただいたページ
- https://learn.microsoft.com/ja-jp/azure/app-service/deploy-staging-slots?tabs=portal
- https://learn.microsoft.com/ja-jp/training/modules/understand-app-service-deployment-slots/4-swap-deployment-slots