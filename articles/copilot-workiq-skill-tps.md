---
title: "GitHub Copilot × Work IQ CLI で業務効率化しよう！　～エンジニアはCLIやVSCodeを使いたい～"
emoji: "🤖"
type: "tech"
topics: ["GitHubCopilot", "WorkIQ", "MCP", "Microsoft365", "AI"]
published: true
---

# はじめに

Microsoft 365 Copilot が「あなたの会議の内容を踏まえると…」と的確に答えてくれたり、2026年3月に発表された **Copilot Cowork** が Outlook やTeams のやり取りを踏まえて自律的にタスクを進めてくれたりしますよね。こうしたエージェントの動作の裏では、**Work IQ** というインテリジェンスレイヤーが動いています。Work IQ が組織の業務データを理解しているからこそ、Copilot やエージェントは「業務を知ったアシスタント」として振る舞えるわけです。

そして Microsoft が 2026年1月にパブリックプレビューとして公開した **Work IQ CLI** は、この Work IQ のインテリジェンスを**開発者のターミナルで使える**ツールです。メールや会議、ドキュメント、Teams メッセージ、組織情報に自然言語でアクセスできます。

https://learn.microsoft.com/ja-jp/microsoft-365/copilot/extensibility/workiq-overview

本記事では、まず **前半** で Work IQ CLI を実際にセットアップして動かします。
**後半** では、GitHub Copilot のカスタマイズ階層（Custom Instructions / Prompt Files / Custom Agents）と組み合わせることで、**属人化しがちなプロンプトや業務知識を Git 管理し、チームで共有して効率化する**ことができます。

:::message alert
本記事の内容は **2026年4月4日時点** の情報に基づいています。Work IQ は現在パブリックプレビューであり、機能や API は変更される可能性があります。
:::

### 参考情報

- [A closer look at Work IQ - Microsoft Tech Community](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/a-closer-look-at-work-iq/4499789)
- [Microsoft Work IQ CLI（preview） - Microsoft Learn](https://learn.microsoft.com/ja-jp/microsoft-365/copilot/extensibility/workiq-overview)
- [Work IQ MCP overview（preview） - Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/use-work-iq)
- [Microsoft Work IQ GitHub リポジトリ](https://github.com/microsoft/work-iq-mcp)
- [Bringing work context to your code in GitHub Copilot - Microsoft Developer Blog](https://developer.microsoft.com/blog/bringing-work-context-to-your-code-in-github-copilot)

---

# 前半：Work IQ CLI を動かしてみる

## そもそも Work IQ って何？

本記事のメインは Work IQ CLI ですが、その前に「Work IQ」自体が何なのかを押さえておきましょう。

https://techcommunity.microsoft.com/blog/microsoft365copilotblog/a-closer-look-at-work-iq/4499789

> Work IQ is the intelligence layer that personalizes Microsoft 365 Copilot to you and your organization.
> （Work IQ は、Microsoft 365 Copilot をあなたと組織に合わせてパーソナライズするインテリジェンスレイヤーです。）

ざっくり言うと、Work IQ は **Microsoft 365 Copilot の裏側で動いている「脳」** です。Copilot が賢く回答できるのは、Work IQ が組織のデータや文脈を理解しているからですね。

### Work IQ の3層アーキテクチャ

Work IQ は以下の3つのレイヤーで構成されています。

| レイヤー | 役割 | 具体例 |
|---------|------|--------|
| **Data** | M365 全体のシグナルを統合 | ファイル、メール、会議、チャット、業務システムからのデータ収集 |
| **Memory** | 人やチームの業務パターンを永続的に理解 | 明示的メモリ（ユーザーが設定）、暗黙的メモリ（チャット履歴から推測）、セマンティックインデックス |
| **Inference** | モデル・スキル・ツールで推論と行動 | MCP ツール呼び出し、エージェントフロー、API 連携 |

たとえるなら、Data 層が「会社中の本棚から情報を集めてくる司書」、Memory 層が「あなたの仕事の癖や優先順位を覚えている秘書」、Inference 層が「集めた情報をもとに考えて行動するアシスタント」という感じです。

この3つが連携することで、Copilot は単なるキーワード検索ではなく、**文脈を理解した意味ベースの検索と推論** ができるようになっています。

### Microsoft の「IQ ファミリー」における位置づけ

Microsoft は Work IQ 以外にも複数の「IQ」を展開しています。

| IQ | 対象領域 | 役割 |
|----|---------|------|
| **Work IQ** | Microsoft 365 | 業務データ（メール、会議、ドキュメント等）の理解とパーソナライズ |
| **Fabric IQ** | データ分析 | データと分析のセマンティックモデル |
| **Foundry IQ** | AI エージェント | エージェントのナレッジとグラウンディング |

Work IQ は「業務情報の流れ」を担当していて、Copilot や各種エージェントがユーザーの仕事を理解するための土台になっています。

## Work IQ CLI とは

ここまでが Work IQ の概念の話で、ここからが **Work IQ CLI** の話です。

Work IQ CLI は、上で説明した Work IQ のインテリジェンスを **開発者のターミナルに直接持ってくる** ツールです。会社の情報に詳しいベテラン社員がターミナルに常駐している感じでしょうか。「あの会議で何が決まったっけ？」「この件、誰に聞けばいい？」みたいな質問を、わざわざ Teams を開かずに聞けるようになります。

具体的には以下の2つのモードで動作します。

| モード | 説明 | 利用シーン |
|--------|------|------------|
| **CLI モード** | `workiq ask` コマンドで直接質問 | ターミナルからのクイック検索 |
| **MCP サーバーモード** | GitHub Copilot や VS Code の AI アシスタントと統合 | コーディング中に業務コンテキストを自動参照 |

ポイントは、Work IQ CLI が単なる検索ツールではなく **MCP サーバー** として動作するところです。つまり、GitHub Copilot の Agent Mode や Custom Agent から「ツール」として呼び出せます。この意味は後半で深掘りします。

アクセスできるデータは、ざっとこんな感じです。

| データ | クエリの例 |
|----------|-----------|
| **メール** | 「XXさんからの依頼を教えて」 |
| **会議** | 「明日の予定を教えて」 |
| **ドキュメント** | 「最近の PowerPoint プレゼンを探して」 |
| **Teams メッセージ** | 「エンジニアリングチャネルの今日のメッセージをまとめて」 |
| **People** | 「プロジェクトYYに関わっているのは誰？」 |

ここで大事なのが、Work IQ CLI は **自分がアクセス権を持っているデータにしかアクセスできない** という点です。

## 前提条件

- **Node.js**（NPX が同梱されている必要あり）
- **Microsoft 365 サブスクリプション**（Copilot ライセンスを含むもの）
- **テナント管理者による同意**（後述の Admin Consent が必要）
- **GitHub Copilot CLI**（CLI 経由で使う場合。オプション）

## セットアップ手順

### Work IQ CLI 単体で使う場合

まずは Work IQ CLI 単体で動かしてみましょう。npm でグローバルにインストールするか、npx で直接実行できます。

```bash
# グローバルインストール
npm install -g @microsoft/workiq
```

```bash
# または npx で直接実行（インストール不要）
npx -y @microsoft/workiq mcp
```

初めて使う前に、エンドユーザーライセンス契約（EULA）に同意する必要があります。

```bash
workiq accept-eula
```

同意すると、ブラウザが開いて Microsoft Entra ID のサインイン画面が表示されます。組織アカウントでサインインしてください。

認証が通れば、`workiq ask` コマンドで早速質問できます。

```bash
# 対話モードで起動
workiq ask

# または直接質問
workiq ask -q "来週月曜日の会議予定を教えて"
```

![](/images/copilot-workiq-skill-tps/2026-04-04-19-39-28.png)


### GitHub Copilot CLI から使う場合

Work IQ CLI 単体でも便利ですが、GitHub Copilot CLI のプラグインとしてインストールすると、**Copilot の推論と組み合わせて使える**のでさらに強力です。

```bash
# Copilot CLI を起動
copilot
```

```bash
# プラグインマーケットプレースの追加（初回のみ）
/plugin marketplace add github/copilot-plugins
```

```bash
# Work IQ プラグインのインストール
/plugin install workiq@copilot-plugins
```

インストールしたら、CLI を再起動します。

```bash
# Ctrl+C で終了後、再度起動
copilot
```

### VS Code での MCP サーバー設定

VS Code から使いたい場合は、MCP 設定ファイルに以下を追加します。

```json
{
  "workiq": {
    "command": "npx",
    "args": ["-y", "@microsoft/workiq", "mcp"],
    "tools": ["*"]
  }
}
```

これで VS Code の GitHub Copilot Chat から Work IQ をツールとして呼び出せるようになります。

---

## 【実録】AADSTS50105 エラーに遭遇する

私の環境（エンタープライズテナント）で私が遭遇したエラーの内容と原因を残しておきます。

サインイン後にこんなエラーが出ました。

```
AADSTS50105: Your administrator has configured the application
Work IQ CLI ('ba081686-5d24-4bc6-a0d6-d034ecffed87') to block users
unless they are specifically granted ('assigned') access to the application.
```

### 原因

これは **Entra ID のエンタープライズアプリケーション設定** に起因するエラーです。

テナント管理者が Work IQ CLI アプリケーションに対して **「ユーザーの割り当てが必要」（Assignment Required = Yes）** を有効にしているため、明示的にアクセス許可されていないユーザーはブロックされます。

### 解決手順

テナント管理者が以下を設定する必要があります。

1. Azure Portal → エンタープライズアプリケーション → 「Work IQ CLI」を検索
2. 「ユーザーとグループ」→「割り当ての追加」
3. 対象ユーザーを選択して割り当て

### WSL2 環境での注意点

もうひとつハマったのが WSL2 環境です。WSL2 の Linux サブシステムから Work IQ を使おうとすると、**デバイス登録ポリシー** に引っかかるケースがあります。WSL2 はエンロール済みデバイスとして認識されないためです。

回避策は、**MCP サーバーを Windows OS 側で起動する** こと。WSL2 から Windows コマンドを直接叩けるので、`powershell.exe` 経由で Node.js / NPX を Windows 側で動かします。

```json
{
  "workiq": {
    "command": "powershell.exe",
    "args": ["-Command", "npx -y @microsoft/workiq mcp"],
    "tools": ["*"]
  }
}
```

この構成なら、WSL2 側の Copilot から MCP サーバーとして接続できます。

---

## `workiq ask` で業務データに聞いてみる

まずは Work IQ CLI 単体の `workiq ask` コマンドで試してみます。

### デモ①：今週の予定を聞く

シンプルなユースケースから始めてみましょう。

```bash
workiq ask -q "今週の会議予定を教えて"
```

![](/images/copilot-workiq-skill-tps/2026-04-04-13-00-07.png)
Work IQ は Microsoft 365 のカレンダーデータにアクセスし、今週の会議一覧を返してくれます。件名、時刻、参加者、場所（Teams リンク含む）が自然言語で整理されて表示されます。

対話モード（`workiq ask` を引数なしで実行）なら、続けてこんな聞き方もできます。

```
You: 明日の会議で準備が必要なものはある？直前のメールもチェックして
```

![](/images/copilot-workiq-skill-tps/2026-04-04-19-45-20.png)

![](/images/copilot-workiq-skill-tps/2026-04-04-19-47-46.png)

**複数のデータソース（カレンダー＋メール）を横断した質問ができる**のが Work IQ のいいところです。Outlook や Teams の業務データをかみ砕いて理解したうえで応答してくれます。

### デモ②：「誰に聞けばいい？」を解決する

大規模組織で地味に時間を食うのが「この技術に詳しい人は誰か」という問いです。新しいプロジェクトに参加したとき、たとえるなら転校生がクラスの人間関係を把握するのに苦労するのと似ています。

```bash
workiq ask -q "生成AIツールの申請について最近ドキュメントを書いた人、または関連する会議に出ていた人は誰？"
```

![](/images/copilot-workiq-skill-tps/2026-04-04-19-53-32.png)

Work IQ はピープルデータ、ドキュメントの編集履歴、会議の参加者情報を横断して、**該当しそうな人物とその根拠**を返してくれます。
びっくりしたのは、AtlassianのConfluenceに書かれたドキュメントの更新者などの情報も拾ってきていたことです。議事録内にあったのか、ドキュメントのプロパティにあったのかはわかりませんが、業務やプロジェクトに対する文脈の理解度がすごいです。驚きました。。。

---

## Copilot 経由で Work IQ を使う

`workiq ask` だけでも十分便利ですが、GitHub Copilot と組み合わせると **Work IQ の検索結果をそのままコード生成やタスク管理に繋げられる** のが大きな違いです。

### デモ③：会議の議事録からアクションアイテムを抽出して Issue 化する

開発現場で最も価値のあるユースケースのひとつだと思います。Copilot CLI で Work IQ プラグインを使って聞いてみます。

```
You: 昨日の「XXX定例」で決まったアクションアイテムをリストアップして
```

![](/images/copilot-workiq-skill-tps/2026-04-04-20-07-33.png)

すると、ask_work_iqのツールが呼び出されることがわかりますね。内容を確認してApproveします。

![](/images/copilot-workiq-skill-tps/2026-04-04-20-09-09.png)

回答結果はこうなります。
![](/images/copilot-workiq-skill-tps/2026-04-04-20-12-27.png)

ここからが Copilot CLI ならではの体験で、**その場でコードに落とし込む** ことができます。

```
You: そのアクションアイテムのうち、設計実装に関するものを GitHub Issue のテンプレートとして書き出して
```

さらにここから、GitHubMCPを使って実際にIssueの登録までやってもらうことも可能です。

「議事録を読む → タスクを整理する → Issue登録」という一連の手作業が、ターミナル上の会話で完結します。`workiq ask` 単体だとテキストの検索・要約で終わりますが、Copilot 経由なら **検索結果を入力にしてコード生成やドキュメント作成まで一気通貫でできる** のが強みです。これ、地味にめちゃくちゃ便利です。

---

# 後半：GitHub Copilot だからこその旨み

## 「便利なプロンプト」の先にある問題

ここまでの前半で、Work IQ CLI の便利さは体感いただけたと思います。ターミナルから会議もメールも検索できる。議事録からタスクも抽出できる。

**でも、こんなことが起きていませんか？**

- 便利だったプロンプトを Slack の自分用チャンネルに貼っている
- 同僚に「こう聞くといいよ」とスクリーンショットを送っている
- 先月いい感じに動いたプロンプトが、今日やったら思い出せない
- チームメンバーが異動したら、ナレッジごと消える

これは**プロンプトの属人化**です。

料理に例えるとわかりやすいかもです。レシピを頭の中だけに持っている料理人は、その人がいないと同じ味が出せない。でもレシピをきちんと書き起こして共有すれば、誰でも同じ料理が再現できるようになります。

コードのバージョン管理が当たり前になったように、プロンプトや業務知識にも「レシピ化」の仕組みが必要です。そして GitHub Copilot には、まさにこの課題を解決する **カスタマイズ階層** が用意されています。

## GitHub Copilot のカスタマイズ階層

GitHub Copilot のカスタマイズは、以下のような階層構造になっています。

| レイヤー | ファイル | スコープ | 役割 |
|----------|----------|----------|------|
| **Organization** | Copilot 設定画面 | 組織全体 | 全リポジトリ共通の開発規約 |
| **Repository** | `.github/copilot-instructions.md` | リポジトリ | プロジェクト固有のルール |
| **Path-specific** | `.github/instructions/*.instructions.md` | ファイルパターン | フロント/バックエンド別の規約 |
| **Prompt Files** | `.github/prompts/*.prompt.md` | 手動呼び出し | 再利用可能なタスクプロンプト |
| **Custom Agents** | `.github/agents/*.agent.md` | 手動選択 | 専門ペルソナ＋ツール制限 |
| **Chat Modes** | `.github/chatmodes/*.chatmode.md` | モード切替 | 行動パターンの切替 |

これらがすべて Markdown ファイルとしてリポジトリにコミットされるので、

- **Git で変更履歴が追える**
- **PR レビューを経て品質が担保される**
- **チームメンバー全員が同じ Skill を使える**
- **フォークすれば他チームにも展開できる**

2026年4月2日に **Organization Custom Instructions が一般提供（GA）** になったことで、組織レベルでの標準化も正式にサポートされました。

## デモ④：前半のプロンプトを `.prompt.md` に Skill 化する

前半のデモ②で使った「議事録からアクションアイテムを抽出する」プロンプトを、再利用可能な Prompt File に変換してみましょう。

### Before：毎回手打ちしていたプロンプト

毎回こんな感じで手打ちしていました。

```
昨日の「XXX定例」で決まったアクションアイテムをリストアップして
```

これだと、会議名のタイプミス、出力フォーマットのばらつき、チームメンバー間での品質差が避けられません。

### After：`.github/prompts/meeting-actions.prompt.md`

```markdown
---
agent: 'agent'
tools: ['workiq/*']
description: '会議のアクションアイテムを抽出して GitHub Issue 化する'
---

## 指示

以下の手順で、指定された会議のアクションアイテムを抽出してください。

1. Work IQ を使って、会議名「${input:meeting_name:会議名を入力}」に
   該当する直近の Teams 会議のトランスクリプトを検索してください。
2. トランスクリプトからアクションアイテムを抽出し、以下の形式で整理してください：
   - 担当者
   - タスク内容
   - 期限（言及があれば）
   - 関連する議論の要約（2-3行）
3. 各アクションアイテムを GitHub Issue のテンプレートとして出力してください。

## 出力フォーマット

各 Issue は以下の構造で出力してください：

### タイトル
[会議名] アクションアイテムの要約

### 本文
- **担当者**: @mention
- **期限**: YYYY-MM-DD
- **背景**: 会議での議論要約
- **完了条件**: 具体的な成果物
```

これで、チームの誰もが Copilot Chat で `/meeting-actions` と入力するだけで、同じ品質のアクションアイテム抽出を実行できます。手打ちの時代と比べると、再現性が段違いですね。

## デモ⑤：`.agent.md` で業務コンテキストエージェントを定義する

Prompt File が「単発タスクのレシピ化」だとすれば、**Custom Agent はツール制限やペルソナを持つ専門料理人を雇う** ようなものです。

Work IQ を MCP ツールとして持つ「業務コンテキストエージェント」を定義してみましょう。

### `.github/agents/biz-context.agent.md`

```markdown
---
name: biz-context
description: >
  M365の業務データ（会議・メール・ドキュメント）を参照しながら、
  ビジネス要件に基づいたコード生成・設計レビューを行うエージェント
tools:
  - workiq/*
  - githubRepo
  - search/codebase
---

あなたはプロジェクトの開発チームをサポートするエージェントです。

## 行動原則

1. **コードを書く前に、必ず業務コンテキストを確認する**
   - 関連する会議の議事録を Work IQ で検索し、要件の背景を理解する
   - 関連するメールスレッドがあれば、ステークホルダーの意図を把握する

2. **既存コードベースとの整合性を担保する**
   - codebase search でプロジェクトの既存パターンを確認する
   - 新規実装が既存アーキテクチャと矛盾しないことを検証する

3. **トレーサビリティを確保する**
   - 生成したコードのコメントに、参照した会議やメールの情報を含める
   - PR の Description に業務コンテキストへのリンクを記載する

## 典型的なワークフロー

ユーザーが「〇〇の機能を実装して」と依頼した場合：

1. Work IQ で「〇〇」に関連する会議・メール・ドキュメントを検索
2. 検索結果から要件・制約・ステークホルダーの意図を整理
3. codebase search で既存の関連コードを確認
4. 要件に基づいてコードを生成
5. テストコードを生成
6. PR の Description ドラフトを作成（業務コンテキストへの参照を含む）
```

このエージェントは Copilot Chat で `@biz-context` と指定するだけで呼び出せます。

```
@biz-context 先週の定例で議論された認証基盤の改修を実装して
```

エージェントは自動的に Work IQ で会議内容を検索し、要件を理解したうえでコードを書き始めます。

**ここが他の AI ツールとの決定的な違いだと思います。** ChatGPT や Claude でも Work IQ MCP は使えます。でも、**エージェント定義がリポジトリにコミットされ、チーム全員が同じペルソナ・同じツール制限で動くエージェントを使える**のは、GitHub Copilot のカスタマイズ階層ならではです。

---

# まとめ

Work IQ CLI や、もちろんMicrosoft Copilot, Coworkは単体でも十分使えます。

今回は、さらにGitHub Copilot のカスタマイズ階層と組み合わると、普段の一連の業務をエージェントに任せる再現性を高め、チームにも共有できることを紹介しました。

- **Prompt File** で「いつも使うあのプロンプト」を全員で共有できる
- **Custom Agent** で「業務コンテキストを理解するエージェント」をリポジトリに定義できる
- **Organization Instructions** で「組織の品質基準」を Coding Agent にまで浸透させられる
- そしてこれらはすべて **Git 管理され、PR レビューで改善され続ける**

普段からGitHubCopilotを使っている技術者が多い環境だと、GitHub Copilot × Work IQ は、その第一歩を踏み出すための組み合わせだと思います。

---

# 参考リンク

- [A closer look at Work IQ - Microsoft Tech Community](https://techcommunity.microsoft.com/blog/microsoft365copilotblog/a-closer-look-at-work-iq/4499789)
- [Microsoft Work IQ CLI（preview） - Microsoft Learn](https://learn.microsoft.com/ja-jp/microsoft-365/copilot/extensibility/workiq-overview)
- [Work IQ MCP overview（preview） - Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/use-work-iq)
- [Microsoft Work IQ GitHub リポジトリ](https://github.com/microsoft/work-iq-mcp)
- [Bringing work context to your code in GitHub Copilot - Microsoft Developer Blog](https://developer.microsoft.com/blog/bringing-work-context-to-your-code-in-github-copilot)
- [GitHub Copilot Custom Instructions - VS Code Docs](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Prompt Files - VS Code Docs](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [Creating Custom Agents - GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents)
- [Organization Custom Instructions GA - GitHub Changelog](https://github.blog/changelog/2026-04-02-copilot-organization-custom-instructions-are-generally-available/)
- [Awesome GitHub Copilot Customizations](https://github.com/github/awesome-copilot)
