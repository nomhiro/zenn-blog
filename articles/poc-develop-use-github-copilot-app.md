---
title: "GAしたGitHub Copilot Appを触ってみた　～Issueから実装・PR・マージまでをエージェントに任せる～"
emoji: "🚀"
type: "tech"
topics: ["githubcopilot", "github", "ai", "agent", "copilot"]
published: true
---

# はじめに

2026年6月17日、**GitHub Copilot app** が GA（一般提供）になりました。Issue を起点に、計画 → 実装 → 動作確認 → PR → マージまでを、エージェントを"監督"しながら回す専用デスクトップアプリです。

- [GitHub Copilot app: The agent-native desktop experience（GitHub Blog）](https://github.blog/news-insights/product-news/github-copilot-app-the-agent-native-desktop-experience/)
- [About the GitHub Copilot app（GitHub Docs）](https://docs.github.com/en/copilot/concepts/agents/github-copilot-app)

簡単に一連の開発の流れに沿って触ってみました。

:::message alert
本記事は **2026年6月時点** の情報です。Copilot app は進化が速いので、画面や機能名は変わっている可能性があります。最新情報は公式ドキュメントを確認してください。
:::

---

# GitHub Copilot app とは

ざっくり言うと、**複数のエージェントセッションを並行で走らせ、監督するためのコックピット**です。ターミナル・IDE・ブラウザ・GitHub を行き来せず、開発ライフサイクル全体をこのアプリ一つで完結させる、というコンセプトですね。

| 概念 | 説明 |
|------|------|
| My Work | アクティブなセッション・Issue・PR・自動化を一覧できるダッシュボード |
| Session | エージェントが作業する独立環境。それぞれ専用の git worktree とブランチを持つ |
| Session mode | `Interactive`（協調）/ `Plan`（計画して承認）/ `Autopilot`（自動実行）の3モード |
| Canvas | 人とエージェントが共同編集する双方向の作業サーフェス（計画・PR・ターミナル・ブラウザなど） |
| Agent merge | CI 監視・レビュアー追跡・チェック対応をしながら、マージまで運んでくれる機能 |

特に効くのが **Session が git worktree で隔離されている**点。並行で複数走らせてもブランチが干渉しません。

それでは触っていきましょーー

---
# 📝 （Option）Step 1: Issue を作成

Issueベースに開発するときを想定して、まずは GitHub 上で Issue を作ります。

やってほしい作業を GitHub の Issue に書き出します。今回立てたのは「ポスターウォール UI のモックを作る（ダミーデータ・Canvas / 統合ブラウザで検証）」。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-25-05.png)

意識したのは、背景・スコープ・受け入れ条件をきちんと書くこと。です。

- 背景: 「観た映画 / ドラマをポスターの棚で眺める」体験の土台を、まずダミーデータで作る
- スコープ: MovieEntry 型、ダミーデータ、PosterCard / PosterGrid / Shelf の実装、描画テスト
- 受け入れ条件: 画面幅で列数が変わる / ポスター欠落時はプレースホルダ / any 禁止 / npm run dev・test・build が通る

この Issue がそのまま「指示書」になります。受け入れ条件を具体的に書くほど「思ってたのと違う」が減る。人間に頼むときと同じですね。

---
# 🗂️ Step 2: Plan モードで計画を立てる

ここから Copilot app。Issue を指定して、まず Plan モードで計画を立ててもらいます。左がエージェントとの対話、右が Canvas。Canvas には plan-canvas.md として「問題 / 目的」「方針」「事前準備（テスト基盤）」「実装スコープ（todos）」がまとまり、右端に実装ステップのチェックリストが並びます。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-25-23.png)

Canvas のいいところは、計画が"成果物"として目の前に出てくること。チャットを遡らなくても、いま何をやろうとしているかが一枚で見えます。しかも読むだけでなく、編集・並び替え・承認ができる双方向のサーフェスです。

Terminal タブに切り替えれば、シェルも触れます。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-25-39.png)

パスが `...\.copilot\repos\copilot-worktrees\movie-shelf\ktc-hirokinomura-silver-fortnight` になっていて、このセッション専用の git worktree で作業しているのが分かります。表で触れた「セッションごとに隔離」が実物で確認できました。

---
# 🤖 Step 3: Autopilot で実装

計画に納得できたら、Autopilot に切り替えて実装をお願いします。ここからはエージェントの自走フェーズ。私は進捗を眺めて、必要なところだけ口を出す係です。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-25-53.png)

進捗は Canvas の Plan で追えます。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-28-21.png)

Setting up test infra → Defining MovieEntry type → Creating sample data → Building PosterCard ... と、計画したステップがそのまま進捗ボードになっています。いまどこを実装中で、あと何が残っているか一目で分かるのはわかりやすいですね！

しばらく眺めるうちに、型定義・ダミーデータ・各コンポーネント・テストまで一通り完成。ここまで手で書いたコードは1行もありません。次は実際に動くか確認します。

---
# 🔍 Step 4: サーバーを起動して動作確認

チェックが全部グリーンでも、テストが通ることと画面がイメージどおりに見えることは別の話。実装中のアプリをそのまま起動して確かめます。

Copilot app には統合ブラウザが内蔵されていて、別のブラウザを開かなくてもアプリ内でプレビューできます。エージェントが開発サーバーを立ち上げ、右側に `movie-shelf` が表示されました。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-29-40.png)

ダミーポスターが格子状に並んでいます。The Grand Budapest Hotel、Spirited Away、Parasite、Blade Runner 2049 ... それぞれにタイトル・公開年・★評価が付き、ポスター画像が欠けたものは「poster」プレースホルダで埋まる。受け入れ条件の「ポスター欠落時はプレースホルダ表示」がそのまま効いています。

左のログでは、エージェント自身も「テストは2回流して通った、build も OK、統合ブラウザで検証できる状態」と整理してくれていました。Issue → 計画 → 実装 → 動作確認 が、アプリを離れずに繋がっているのが体感できます。

---
# 🔀 Step 5: PR を作成

見た目も挙動も問題なさそうなので、PR を作ってもらいます。画面右上のボタンを押すと「Creating PR…」に変わり、作成が走り出しました。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-35-33.png)

上部のタブには Changes（+1455 / -265）、Plan、Terminal、plan-canvas.md、preview と、このセッションの成果物が並びます。アドレスバーが `localhost:5174` を指していて、さっきの統合ブラウザがここに紐づいているのも分かります。

PR 作成の中身は左のログで追えます。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-37-57.png)

「まず変更をコミット・プッシュします」と宣言してから、

- `git status` で変更を確認
- `.github` 配下の PULL_REQUEST_TEMPLATE を探し、テンプレートに沿って本文を用意
- 変更をコミット
- ブランチを push して upstream を設定
- PR を作成（`ktc-hirokinomura/poster-wall-mock → origin/main`）

を順にこなし、最後に「PR を作成しました。コミット・プッシュ済みで、npm test / build / lint すべて green です」と報告。

---
# 🚀 Step 6: Agent merge でマージ

最後はマージ。Canvas に切り替えると、作成された PR の中身がそのまま読めます。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-51-42.png)

PR 本文には、フィルター / 並び替えのロジックの置き場所、テスト基盤に Vitest を選んだこと、検証結果（npm test 11 passed、build 成功、lint クリーンで any 不使用）まで過不足なくまとまっています。AGENT.md の分離方針（表示は src/components、ロジックは src/lib、データは src/mocks）も守られ、「実データ（library.json）への接続は別 Issue（#4）で対応予定」とスコープ外の宣言まで添えてありました。下の Check Status では CI / build が pull_request・push の両方で成功。GitHub Actions の生ログまでは追えませんが、状態把握には十分です。

そして今回一番触ってみたのが **Agent merge**です。「Merge pull request」の隣のトグルです。

![](/images/poc-develop-use-github-copilot-app/2026-06-09-23-53-27.png)

> Agent will address reviews, fix CI, and resolve conflicts automatically.

レビュー指摘への対応・CI の修正・コンフリクト解消までエージェントがやってくれる機能です。今回は Ready to merge / All checks passed / Unresolved review comments 0 と問題ない状態だったので、そのままマージしました。

---
# まとめ

`movie-shelf` の「ポスターウォール UI のモックを作る」Issue を題材に、

Issue 作成 → Plan で計画 → Autopilot で実装 → 統合ブラウザで動作確認 → PR 作成 → Agent merge でマージ

を、ほぼアプリ一つの中で回してみました。

Issue を書いてからは、ほとんどこのアプリから出ずに作業できました。コードを書く速さより、何を作るかを言語化する力（Issue と AGENT.md を整える力）のほうが効いてくるな、と改めて思いました。