---
title: "Durable Task Scheduler"
emoji: "📘"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

## 関数アプリの作成
関数アプリのリソースを作成します。
ホスティングオプションはAppServiceを選択します。
![](/images/functions-durable-task-scheduler/2025-05-09-21-24-28.png)

今回はOSはLinux、ランタイムはPythonにします。
リージョンはJapanEastです。
![](/images/functions-durable-task-scheduler/2025-05-09-21-33-17.png)

関数アプリが動作するためのストレージアカウントを指定します。
![](/images/functions-durable-task-scheduler/2025-05-09-21-34-37.png)

ネットワークは今回はパブリックアクセスを有効にします。
![](/images/functions-durable-task-scheduler/2025-05-09-22-06-11.png)

アプリケーション監視のためのApplication Insightsを有効にします。
![](/images/functions-durable-task-scheduler/2025-05-09-22-06-55.png)

Durable Functionsの設定をします。**ここでDurable Task Schedulerを選びます。**
![](/images/functions-durable-task-scheduler/2025-05-09-22-10-03.png)

継続的デプロイは無効にします。VSCodeから手動でデプロイします。
![](/images/functions-durable-task-scheduler/2025-05-09-22-12-56.png)

認証はデフォルトのままです。
![](/images/functions-durable-task-scheduler/2025-05-09-22-15-45.png)

確認してデプロイしましょう。
![](/images/functions-durable-task-scheduler/2025-05-09-22-17-02.png)

![](/images/functions-durable-task-scheduler/2025-05-09-22-17-18.png)
