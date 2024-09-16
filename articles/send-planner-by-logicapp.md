---
title: "Azure Logic AppでMicrosoft Plannerと連携しよう！"
emoji: "📅"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "LogicApp", "Planner"]
published: false
---

![](/images/send-planner-by-logicapp/2024-09-16-12-30-50.png)

# 背景
Microsoft Plannerは、Microsoft 365の一部として提供されるタスク管理ツールです。これを使うことで、チームや個人のタスクを管理できます。Teamsからも利用できるため、チーム内でのタスク管理に便利です。

### この記事のモチベーション
もちろん、TeamsやPlannerのWebアプリから、手動でタスクを登録することができます。
**何らかのWebアプリなどからシステム的にPlannerと連携するには、API経由で登録したいです。**
主に2つの方法がありそうです。
- GraphAPIを使う
  - @[card](https://learn.microsoft.com/ja-jp/graph/planner-concept-overview)
- **LogicAppを使う**
  - @[card](https://learn.microsoft.com/ja-jp/connectors/planner/)

この記事では、LogicAppを使ったPlannerへのタスク登録を行います。

# Microsoft Plannerを使う

Microsoft 365を契約している場合、Microsoft Plannerを使うことができます。
https://www.microsoft.com/ja-jp/microsoft-365/planner/microsoft-planner-plans-and-pricing

契約していない場合、試用版のMicrosoft Plannerを使います。
https://www.microsoft.com/ja-jp/microsoft-365/planner/microsoft-planner?msockid=3af131bd8d5365ea342825718cd86476

:::details 試用版のMicrosoft Plannerを使う手順

「無料で試す」をクリック
![](/images/send-planner-by-logicapp/2024-09-16-08-49-00.png)

メールアドレスを入力して「次へ」
![](/images/send-planner-by-logicapp/2024-09-16-08-48-47.png)

「アカウントのセットアップ」
![](/images/send-planner-by-logicapp/2024-09-16-08-50-31.png)

アカウント情報を入力し「次へ」
![](/images/send-planner-by-logicapp/2024-09-16-08-52-54.png)

セキュリティチェック実施
![](/images/send-planner-by-logicapp/2024-09-16-08-59-16.png)

ドメイン名とユーザ名、作成するアカウントのパスワードを入力
![](/images/send-planner-by-logicapp/2024-09-16-09-00-37.png)

支払方法を追加
※アカウントにカードを紐づける必要があるが、Plannerの試用版は無料です。
![](/images/send-planner-by-logicapp/2024-09-16-09-04-43.png)

「作業の開始」
![](/images/send-planner-by-logicapp/2024-09-16-09-10-43.png)

試用版のMicrosoft 365が利用できるようになります。
![](/images/send-planner-by-logicapp/2024-09-16-09-12-42.png)

https://tasks.office.com
右下の「サインイン」
アカウントを作成した直後は、以下のように表示されます。しばらく待ってから再度アクセスしましょう。
![](/images/send-planner-by-logicapp/2024-09-16-09-18-52.png)
:::

# LogicAppでPlannerにタスク登録する

## LogicAppの作成
「追加」をクリック
![](/images/send-planner-by-logicapp/2024-09-16-10-01-29.png)

「従量課金」を選択
![](/images/send-planner-by-logicapp/2024-09-16-10-02-03.png)

以下を設定しましょう。
- サブスクリプション
- リソースグループ
- アプリ名
- リージョン
![](/images/send-planner-by-logicapp/2024-09-16-10-04-09.png)

内容を確認して、作成します。
![](/images/send-planner-by-logicapp/2024-09-16-10-05-54.png)

作成完了！！！🎉
![](/images/send-planner-by-logicapp/2024-09-16-10-06-28.png)

## Plannerに登録する処理

さて、ここからが本題です。以下のフローを作成していきます。
1. HTTPトリガー（POST）でタスク名と期限日を受け取る
2. Plannerにタスクを登録する
3. HTTPレスポンスを返す

### HTTPトリガー（POST）の設定

「ロジックアプリデザイナー」で、「トリガーの追加」をクリック
「When a HTTP request is reveived」を選択
![](/images/send-planner-by-logicapp/2024-09-16-10-09-06.png)


「サンプルのペイロードを使用してスキーマを生成する」をクリック。
Bodyで受け取りたいJson構造を定義します。
タスク名、期限日を受け取るため、以下のように設定します。
```json
{
   "task": {
      "name": "task name",
      "dueDate": "2024-09-16T10:00:00Z"
   }
}
```

![](/images/send-planner-by-logicapp/2024-09-16-11-07-59.png)

以下のように自動でBody部のスキーマが設定される。
Methodは「POST」を選択します。
![](/images/send-planner-by-logicapp/2024-09-16-11-09-28.png)

### Responseの設定
「＋」をクリックして、「アクションの追加」します。
![](/images/send-planner-by-logicapp/2024-09-16-11-14-08.png)

「Response」で検索しクリック
![](/images/send-planner-by-logicapp/2024-09-16-11-14-36.png)

Headersに以下を設定します。
- Key: Content-Type
- Value: application/json
Bodyに以下を設定
- Body (triggerBody())
![](/images/send-planner-by-logicapp/2024-09-16-11-17-44.png)

### HTTPTrigger 稼働確認

いったん、HTTPTriggerとResponseが問題なく動くかを確認します。
作成したフローを保存します。
![](/images/send-planner-by-logicapp/2024-09-16-11-19-03.png)

「ペイロードで実行」をクリックし、Bodyを設定し実行します。
![](/images/send-planner-by-logicapp/2024-09-16-11-21-10.png)

「実行履歴」の画面で、実行結果をクリックします。
![](/images/send-planner-by-logicapp/2024-09-16-11-20-49.png)

Responseの詳細を確認すると、ResponseのBodyにRequestのBodyがそのまま返ってきていることが確認できます。
![](/images/send-planner-by-logicapp/2024-09-16-11-22-41.png)

### Plannerにタスク登録する処理追加
HTTPTriggerの次にPlannerにタスク登録する処理を追加します。
![](/images/send-planner-by-logicapp/2024-09-16-11-23-52.png)

「タスクを作成する（Preview）」を選択します。
![](/images/send-planner-by-logicapp/2024-09-16-11-25-02.png)
:::message
プレビュー版では、タスクの優先度を設定できるようになっています。
- 有効な値の範囲は0〜10 (両端を含む) 
- 値を大きくすると優先度が低い。0 が最優先度、10 が最低の優先度
- Plannerでは、0 と 1 の値を 「緊急」、2、3 および 4 を 「重要」、5、6 および 7 を 「中」、8、9 および 10を 「低」 と解釈する。

@[card](https://learn.microsoft.com/ja-jp/connectors/planner/#%E3%82%BF%E3%82%B9%E3%82%AF%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B-(%E3%83%97%E3%83%AC%E3%83%93%E3%83%A5%E3%83%BC))
:::

Plannerにサインインします。
Plannerが使えるアカウントでサインインしてください。
![](/images/send-planner-by-logicapp/2024-09-16-11-44-05.png)

Plannerでタスク登録する対象の「グループ」と「プラン」を選択し、フローを保存します。
![](/images/send-planner-by-logicapp/2024-09-16-11-55-23.png)

### タスク登録処理の稼働確認
ペイロードで実行し、Plannerにタスクが登録されることを確認します。
Bodyには以下を設定します。
```json
{
   "task": {
      "name": "LogicAppでPlannerにタスク登録する処理の追加",
      "dueDate": "2024-09-17T13:00:00Z"
   }
}
```
![](/images/send-planner-by-logicapp/2024-09-16-12-03-45.png)

Plannerにタスクが登録されました！🚀
![](/images/send-planner-by-logicapp/2024-09-16-12-05-17.png)