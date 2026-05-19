---
title: "Cosmos DB Shell と CosmosDB MCP サーバー を試してみた。～ × GitHub Copilot～"
emoji: "🐻‍❄️"
type: "tech"
topics: ["azure", "cosmosdb", "githubcopilot", "mcp", "ai"]
published: true
---

# はじめに

2026年5月に Azure Cosmos DB Shell のパブリックプレビューが発表されました。VS Code 拡張として動く CLI/シェルなのですが、**MCP サーバー機能** も同梱されています。

https://devblogs.microsoft.com/cosmosdb/azure-cosmos-db-shell-public-preview-ai-mcp-cli/

つまり、VS Code の GitHub Copilot から「Cosmos DB に対してクエリを叩く道具」としてエージェントに渡せる、ということですね。

そこで今回は、AIエージェントを介して自然言語だけでデータベースにクエリを投げて分析するネタでこのツールを使ってみました。

:::message
本記事の内容は **2026年5月11日時点** の情報に基づいています。Cosmos DB Shell はパブリックプレビューであり、機能や設定は変更される可能性があります。
:::

### 参考情報

- [Azure Cosmos DB Shell Public Preview 発表記事](https://devblogs.microsoft.com/cosmosdb/azure-cosmos-db-shell-public-preview-ai-mcp-cli/)
- [Cosmos DB Shell GitHub リポジトリ](https://github.com/Azure/CosmosDBShell)
- [Cosmos DB Shell ドキュメント](https://learn.microsoft.com/en-us/azure/cosmos-db/shell/overview)

---

# Azure Cosmos DB Shell とは

ざっくり言うと、**VS Code の中で動く Cosmos DB 用のシェル** です。`ls`、`cd database-name` のような感覚でデータベース・コンテナを行き来できて、SQL クエリも直接叩けます。

**MCP サーバーも内蔵されています。**　`settings.json` でフラグを立てるだけで、GitHub Copilot からツール経由で Cosmos DB を扱えるようになります。

## セットアップ

セットアップは非常に簡単です。

1. VS Code に Cosmos DB Shell 拡張をインストール
![](/images/poc-cosmosdb-shell/2026-05-11-22-15-19.png)

2. `settings.json` に MCP の設定を追加

```json
{
  "cosmosDB.shell.MCP.enabled": true,
  "cosmosDB.shell.MCP.port": 6128,
  "cosmosDB.shell.MCP.startOnLaunch": true,
  "cosmosDB.shell.MCP.bindToLocalhost": true
}
```

3. Launch Azure Cosmos DB Shell でシェルを起動
![](/images/poc-cosmosdb-shell/2026-05-11-22-15-42.png)

なお、初回起動時には .NET SDK の要求が出ます。

![](/images/poc-cosmosdb-shell/2026-05-11-20-39-14.png)

`Install .NET SDK` を押せば勝手に入れてくれます。

4. GitHub Copilot 側で MCP サーバーとして登録

これだけです。あとは Copilot Agent モードを開いて、ツール一覧に Cosmos DB Shell が出ていれば準備完了です。

---

# 試したユースケース：架空のレンタカー会社で経営判断

題材は **架空のレンタカー会社「しろくまレンタカー」** にしました。設定はこんな感じです。

- 全国 30 店舗、車両保有 約 500 台
- 車種クラス: `compact` / `suv` / `minivan` / `ev` / `luxury`
- Cosmos DB に **過去 2 年分の予約 約 5 万件、ユーザー 1.5 万人、店舗 30 件** を投入済み


> 来週の経営会議で次年度の車両投資計画を出してほしい。今のクラス構成のままでいいのか、データから示唆をください。cosmosdb mcp だけを使ってデータ取得したうえで、データ分析してレポートにして。

※もちろん分析の軸とかの方向性を示したほうがいいですが、あえてGitHubCopilot任せにしてみましょー

## データに仕込んだ「罠」

これ、ただクエリを投げても面白い記事にならないので、データに**「単純に売上ランキングだけ見ると間違える」仕掛け**を埋め込んでおきました。

具体的にはこんな構造です。

| 車種 | 予約シェア | 稼働率 | ARPU/日 | 前年比成長 | リピート率 |
|---|---|---|---|---|---|
| compact | 40% | 93% | 6,000円 | +5% | 35% |
| suv | 25% | 60% | 9,000円 | +10% | 40% |
| minivan | 15% | 45% | 12,000円 | +3% | 30% |
| **ev** | **8%（前年3%）** | **80%超（地方店舗）** | 8,000円 | **+122%** | **50%** |
| luxury | 12% | 13% | 25,000円 | -5% | 25% |

売上ランキングだけ見ると「コンパクトを増やせ」となりがちですが、実は **EV が地方店舗で爆伸びしている**、**ラグジュアリーは ARPU で売上を稼いでいるだけで稼働率は壊滅的**、というような構造を仕込んでいます。

エージェントがここを多軸で見て覆せるかどうかが、試してみましょう～

---

# 実際にやってみた

これをGitHubCopilotのエージェントモードで聞いてみます。
```
来週の経営会議で次年度の車両投資計画を出してほしい。今のクラス構成のままでいいのか、データから示唆をください。
cosmosdb mcp だけを使ってデータ取得したうえで、データ分析してレポートにして。
```

例の一行を Copilot Agent に投げた後の、実際の動きを抜粋して紹介します。

:::details エージェントの動き全文
```bash
ここからはデータ取得を Cosmos DB MCP のみに限定して、経営判断に必要な集計を順に取ります。まず予約・店舗・顧客の主要指標を直接クエリできるようにします。



まず経営判断の芯になる集計を一括で取り、そこから深掘り対象を絞ります。ここではクラス別実績、ノイズ率、店舗別の供給、店舗×クラス需要を取ります。

Ran Run Query 
Completed with input: {
  "query": "SELECT c.carClass, COUNT(1) AS reservations, SUM(c.amount) AS revenue, AVG(c.amount / c.rentalDays) AS arpuPerDay, SUM(c.rentalDays) AS rentalDays FROM c WHERE c.status = 'completed' GROUP BY c.carClass",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.status, COUNT(1) AS reservations FROM c GROUP BY c.status",
  "max": 20,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.id, c.region, c.fleetCount FROM c",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "stores"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.pickupStoreId, c.carClass, COUNT(1) AS reservations, SUM(c.rentalDays) AS rentalDays, SUM(c.amount) AS revenue FROM c WHERE c.status = 'completed' GROUP BY c.pickupStoreId, c.carClass",
  "max": 500,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

現状の概況は取れました。次は投資判断に直結する 4 点、稼働率、前年比、EV の地域偏在、ミニバン週末偏重を絞って取ります。

Created 3 todos

次のバッチでは、前年比と長期比率、曜日偏重、EV 地域偏在を直接取って結論の根拠を固めます。うまくいかなければ一段ずつ関数互換のある形に落とします。

Ran Run Query 
Completed with input: {
  "query": "SELECT c.carClass, COUNT(1) AS reservations, SUM(c.amount) AS revenue FROM c WHERE c.status = 'completed' AND c.pickupAt >= '2025-05-12T00:00:00Z' GROUP BY c.carClass",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.carClass, COUNT(1) AS reservations, SUM(c.amount) AS revenue FROM c WHERE c.status = 'completed' AND c.pickupAt < '2025-05-12T00:00:00Z' GROUP BY c.carClass",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.carClass, COUNT(1) AS reservations, SUM(IIF(c.rentalDays >= 7, 1, 0)) AS longReservations FROM c WHERE c.status = 'completed' GROUP BY c.carClass",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT DateTimePart('dw', c.pickupAt) AS weekday, COUNT(1) AS reservations FROM c WHERE c.status = 'completed' AND c.carClass = 'minivan' GROUP BY DateTimePart('dw', c.pickupAt)",
  "max": 20,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

最後の根拠として、直近 1 年の稼働日数と EV の店舗偏在を取ります。これで「どこに何を増やすか」まで落とせます。

Ran Run Query 
Completed with input: {
  "query": "SELECT c.carClass, SUM(c.rentalDays) AS rentalDays FROM c WHERE c.status = 'completed' AND c.pickupAt >= '2025-05-12T00:00:00Z' GROUP BY c.carClass",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.pickupStoreId, COUNT(1) AS reservations, SUM(c.rentalDays) AS rentalDays, SUM(c.amount) AS revenue FROM c WHERE c.status = 'completed' AND c.carClass = 'ev' AND c.pickupAt >= '2025-05-12T00:00:00Z' GROUP BY c.pickupStoreId",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

Ran Run Query 
Completed with input: {
  "query": "SELECT c.pickupStoreId, COUNT(1) AS reservations, SUM(c.rentalDays) AS rentalDays, SUM(c.amount) AS revenue FROM c WHERE c.status = 'completed' AND c.carClass = 'luxury' AND c.pickupAt >= '2025-05-12T00:00:00Z' GROUP BY c.pickupStoreId",
  "max": 100,
  "metrics": "Display",
  "format": "json",
  "bucket": 0,
  "database": "shirokuma-rental",
  "container": "reservations"
}

集計根拠は揃ったので、経営会議向けにそのまま読めるレポートへ落とし込みます。内容は Cosmos DB MCP で取った数値だけを根拠にします。

Generating patch (172 lines) in [](file:///c%3A/Users/HirokiNomura/workspaces/nomhiro/poc-cosmos-db-shell/docs/vehicle-investment-report.md)


```

```
レポート本文を追加したので、差分だけ確認して数値や論旨の崩れがないかを見ます。Markdown なので実行系の検証はなく、ここでは内容差分を絞って確認します。

Ran terminal command: git diff -- docs/vehicle-investment-report.md
Completed with input: git diff -- docs/vehicle-investment-report.md

差分確認は、このフォルダが Git 管理下ではないため使えませんでした。代わりに生成ファイルの存在と主要数値の埋め込みをピンポイントで確認します。

Ran terminal command: Select-String -Path docs/vehicle-investment-report.md -Pattern '93.4%|122.4%|80.4%|101.7%|66.2%|13.2%'

数値入りのレポート生成と内容確認までは完了しました。残りは、ユーザー向けに要点と前提を短く整理して返します。

Completed: *投資判断指標を深掘り* (2/3)

経営会議向けのレポートを作成しました。データ取得は Cosmos DB MCP の read-only クエリだけで行っています。レポート本体は vehicle-investment-report.md です。

要点だけ先にまとめると、今のクラス構成をそのまま維持する判断は非推奨です。追加投資は一律ではなく、クラスと地域を分けるべきでした。compact は稼働率 93.4% でほぼ飽和なので更新中心、ev は前年同期比 122.4% 増かつ東北・北海道・九州だけで予約の 80.4% を占めるため地方限定で増車、suv は 7日以上比率 27.7% の長期需要を拾えているので優先投資、luxury は稼働率 13.2% と低すぎるため縮小が妥当、という結論です。minivan は週末依存 66.2% が強く、増車より平日需要の施策が先です。

レポート内には、クラス別売上、近似稼働率、前年比、長期レンタル比率、EV の店舗偏在、minivan の曜日偏重まで根拠を入れてあります。主要数値が反映されていることも確認済みです。必要なら次に、1. このレポートを経営会議用の1ページ要約に圧縮する 2. PRD の Step 1-8 に沿った対話ログ風の分析記事へ展開する、のどちらかまで続けます。

Made changes.
```
:::


## まずは全体像の把握から

まず最初に全体像を把握するために、**4本のクエリを並行投入**してきました。
クラス別実績、ノイズ率（cancelled / failed 比率）、店舗別の供給、店舗×クラス需要、という分析の地盤になる集計です。

![](/images/poc-cosmosdb-shell/2026-05-11-22-26-45.png)

## 段階的に深掘り

最初の集計を取った後、エージェントは Todo リストを自分で作って「次のバッチでは、前年比と長期比率、曜日偏重、EV 地域偏在を直接取って結論の根拠を固めます」と宣言。続けて以下のクエリをまとめて投げました。

```sql
-- 前年比（直近1年）
SELECT c.carClass, COUNT(1) AS reservations, SUM(c.amount) AS revenue
FROM c
WHERE c.status = 'completed' AND c.pickupAt >= '2025-05-12T00:00:00Z'
GROUP BY c.carClass
```

```sql
-- 長期レンタル比率（7日以上）
SELECT c.carClass, COUNT(1) AS reservations,
       SUM(IIF(c.rentalDays >= 7, 1, 0)) AS longReservations
FROM c
WHERE c.status = 'completed'
GROUP BY c.carClass
```

```sql
-- ミニバンの曜日偏重
SELECT DateTimePart('dw', c.pickupAt) AS weekday, COUNT(1) AS reservations
FROM c
WHERE c.status = 'completed' AND c.carClass = 'minivan'
GROUP BY DateTimePart('dw', c.pickupAt)
```

```sql
-- EV の店舗偏在
SELECT c.pickupStoreId, COUNT(1) AS reservations,
       SUM(c.rentalDays) AS rentalDays, SUM(c.amount) AS revenue
FROM c
WHERE c.status = 'completed' AND c.carClass = 'ev'
  AND c.pickupAt >= '2025-05-12T00:00:00Z'
GROUP BY c.pickupStoreId
```

ちゃんと、 **`IIF` や `DateTimePart` のような Cosmos DB の組み込み関数をちゃんと使い分けてくれてますね**

## エージェントが出した結論

集計を取り終えたエージェントは、最終的に Markdown のレポートを生成してきました。要点はこうです。

| 車種 | 推奨アクション | 根拠 |
|---|---|---|
| compact | **更新中心**（増車しない） | 稼働率 93.4% で既に飽和、前年比も +5% で頭打ち |
| ev | **地方店舗中心に増車** | 前年同期比 +122.4%、東北・北海道・九州で予約の 80.4% を占める |
| suv | **優先投資** | 7日以上比率 27.7%、家族旅行・長距離の安定需要 |
| minivan | **増車より平日施策が先** | 週末依存 66.2%、平日活用の法人プラン等とセットで検討 |
| luxury | **縮小** | 稼働率 13.2% と低すぎ。SUV に振り向ける |

「現状のクラス構成を維持する判断は非推奨」という結論まで添えて、根拠数値を引用しながら 1 ページのレポートにまとめてくれました。

データから示唆を引き出しただけでなく、**「一律ではなく分けるべき」というアクションの方向性まで踏み込んでくれてます。**

---

# まとめ

作業ループが IDE 内で完結するので楽ですね。

1. ポータルか拡張で Cosmos DB を開く
2. クエリを書く
3. 結果をコピーして AI に渡す
4. 解釈してもらう
5. 次のクエリを考えてまた書く

という行ったり来たりが必要でした。それが **「ビジネス課題を投げる」→「エージェントがクエリを書き、結果を見て、次のクエリを考える」** というループを VS Code の中だけで回せます。

---

Cosmos DB for NoSQL は RDB と違って JOIN が苦手なので、複数コンテナを横断する集計は人間が手で組み立てる必要があります。今回も「予約 × 店舗マスタ」「予約 × ユーザーマスタ」みたいな突合が必要でしたが、エージェントが片方ずつクエリしてから自分の頭の中で突き合わせる、という分担を勝手にやってくれます。

「コンテナを分けたから後で繋ぐのが面倒…」という Cosmos DB あるあるの心理的ハードルが、けっこう下がる気がします。

---

# 所感とハマりどころ

良かった点ばかりではないので、触っていて気になったところも書いておきます。

- **read-only に絞る運用は必須**。今回は MCP 経由のクエリのみに限定しましたが、書き込み系の操作も技術的にはできてしまうので、本番データに繋ぐときは権限設計が必要です
- **クエリ結果のトークン消費**は地味に重い。集計済みの小さな結果ならいいのですが、`SELECT *` を投げられると一発で context を食います。エージェントへの初期プロンプトで「集計を中心に取って」と方向付けしておくと安定しました
- 大規模分析を見据えるなら **Analytical Store / Fabric / Synapse 連携** の世界が別途あります。今回みたいに数万件レベルの探索なら MCP 直叩きで十分ですが、数百万件超で同じことをやるなら別の道具になります


また、当たり前の話ではありますが、、、
今回は雑なプロンプトだけで自律的なエージェントに任せましたが、繰り返しの業務や確実な勝利が必要な場合は、MCPサーバと自前のスクリプトを組み合わせたり、Skillsにして再現性を高めるのがよいでしょう。