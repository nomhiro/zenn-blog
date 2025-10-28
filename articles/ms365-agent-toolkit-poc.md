---
title: "Microsoft 365 Agents Toolkit [1] ~入門~"
emoji: "💭"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["agenttoolkit", "microsoft365", "copilot", "teams"]
published: false
---

# 概要

Microsoft 365 Agents Toolkit は、Microsoft 365 CopilotやTeams、Officeなどで動作する**エージェントとアプリを開発するためのツールキット**です。前身はTeams Toolkitです。
作成したエージェントやアプリをパッケージ化、配布、管理される Office アドイン全体で実行される統合アプリを構築できるようになります。Microsoft 365 Agents SDKが含まれているので、**M365 CopilotやTeams、OfficeなどのMicrosoft 365製品と連携したアプリケーションを公開**できます。

https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/build-and-test/tool-sdk-overview

本記事では、Microsoft 365 Agents Toolkit の概要を把握しながら、Actionを持たないシンプルな Agentを作成してみます。

:::message alert
この記事で作成するActionやAzureとの連携がないエージェントであれば、Microsoft 365 Copilot画面から作成するエージェントとできることは同じです。まずは**Microsoft 365 Agents Toolkit の使い方を理解する**ことを目的としています。
:::


# Toolkitの概要

- **Build a Declarative Agent**：宣言的エージェントを構築します。
  - **宣言的エージェント**とは、その名の通りエージェントのふるまいを宣言的にJSONファイルで定義して、Copilotはその仕様に従って動作するエージェントのことです。
  - コードを書かずに、設定ファイルのみでエージェントを作成できます。
- **Create a New Agent/App**：新しいエージェントやアプリを作成します。
  - **Declarative Agent**：設定ベースのエージェント（今回作成するもの）
  - **Imperative Agent**：JavaScript/TypeScriptでロジックを記述するエージェント
  - **Teams App**：従来のTeamsアプリケーション
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-02-31.png)

## Azureとの連携

MS365 Copilotなどでエージェントを作成していると、既存アプリとの連携やデータベースとの接続など、エージェントがCopilot以外のサービスと連携する必要が出てきます。
Agents Toolkitでは、**Azure Functions の HTTPトリガーなどの API を Declarative Agent の OpenAPI アクションとして宣言し、Copilot（Agents）から呼び出す**ように設定できます。

![](/images/ms365-agent-toolkit-poc/2025-10-28-21-21-47.png)

---

# 環境設定

## 前提条件

以下の環境が必要です：
- **Microsoft 365 Business Premium** または **Enterprise** ライセンス（Copilotライセンス含む）
- **開発者権限**またはテナント管理者権限
- Microsoft 365アカウント（またはMicrosoft 365 Developer Program のSandboxアカウント）

### VSCode に 拡張機能をインストール

VSCodeにMicrosoft 365 Agents Toolkit拡張機能をインストールします。

![](/images/ms365-agent-toolkit-poc/2025-10-28-20-59-27.png)

### Teamsアプリを構築するために必要なツール

- [Node.js](https://nodejs.org/en/download/)
- npm
- VSCode の拡張機能「Azure Tools」
- React JavaScript ライブラリ用のブラウザー DevTools 拡張機能
  - [Chrome用](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
  - [Edge用](https://microsoftedge.microsoft.com/addons/detail/react-developer-tools/gpphkfbcpidddadnkolkpfckpihlkkil)

# 🚀シンプルなDeclarative Agentの作成

まずは、ActionなどがないシンプルなDeclarative Agentを作成してみます。
業務上で、ある新たなアイデアを思い付いたときに、そのアイデアをブラッシュアップしてくれるエージェントを作成してみましょう！

### プロジェクトの作成

Agents Toolkitのメニューから「Create a New Agent/App」をクリックします。
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-41-57.png)

「Declarative Agent」（宣言型エージェント）を選択します。
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-43-23.png)

エージェントに追加するアクションは、「No Action」を選びます。
:::details 選択肢の解説
- **No Action**：アクションを持たないシンプルなエージェントを作成します。
- **Add an Action**：アクションを追加してエージェントを作成します。
- **Add a Copilot connector**：Copilotコネクタを追加してエージェントを作成します。
- **Start with TypeSpec for Microsoft 365 Copilot**：TypeSpecを使用してエージェントを作成します。
:::
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-48-20.png)

フォルダを選択します。
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-49-04.png)

アプリケーション名を入力します。
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-55-07.png)

作成が完了すると、以下のようなフォルダ構成でプロジェクトが作成され、指定したフォルダでVSCodeが起動します。
![](/images/ms365-agent-toolkit-poc/2025-10-28-21-56-34.png)

### エージェントの指示

`appPackage\instruction.txt` にエージェントへの指示を記述します。今回は、アイデアをブラッシュアップする企画書作成エージェントを作成するので、以下のように記述します。
:::message
- いわゆる**システムプロンプト**です。エージェントの役割、動作方法、Actionの使い方、出力フォーマット、制約事項などを記述します。
- **8,000 文字以下**という制限があります。
- プロンプトエンジニアリングの知識が活用できる箇所です。
:::

```txt
あなたは「アイデアブラッシュアップ＆企画書作成エージェント」です。
ユーザーが入力した業務アイデアを整理し、簡潔な企画書にまとめます。

【役割】
- アイデアをポジティブに評価
- 改善ポイントを3〜5項目提案
- 目的・効果・実施計画を簡潔に記載
- Markdown形式で企画書を生成

【出力フォーマット】
# 企画書タイトル
## 1. 背景
## 2. 目的
## 3. 提案内容
## 4. 期待効果
## 5. 実施計画（簡易）
## 6. 次のアクション

【ルール】
- 文体はシンプルで丁寧
- 数字や期間は仮置きでも明示
- 不足情報は質問して補う
- 最後に「改善提案リスト」を箇条書きで追加

【例】
ユーザー：「社内イベントを企画したい」
エージェント：
- ポジティブコメント
- 改善提案（例：目的明確化、参加者メリット、コスト試算）
- 上記フォーマットで企画書を生成
```

### エージェントの定義

ここはエージェントのふるまいとは関係ありませんが、エージェントの説明や表示内容などを appPackage\declarativeAgent.json の description に記述します。
- **name**: エージェントの名前
- **description**: エージェントの説明
- **instructions**: 先ほど作成した instruction.txt を参照
- **conversation_starters**: エージェントの会話のきっかけとなる例文

```json
{
    "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.5/schema.json",
    "version": "v1.5",
    "name": "アイデアブラッシュアップ＆企画書作成エージェント",
    "description": "業務アイデアを整理し、簡潔な企画書（Markdown）を生成します。改善ポイント提案と次アクションを含みます。",
    "instructions": "$[file('instruction.txt')]",
    "conversation_starters": [
        { "title": "社内イベントの企画", "text": "参加者のメリットを明確化した社内イベント企画書を作って" },
        { "title": "業務フロー改善", "text": "営業の見積フロー簡略化の企画書を作成して" },
        { "title": "ナレッジ共有施策", "text": "部門横断のナレッジ共有施策を提案して" }
    ]
}
```

そのほかの定義についてはこちらに記述されています。
https://learn.microsoft.com/ja-jp/microsoft-365-copilot/extensibility/declarative-agent-manifest-1.5?tabs=json#declarative-agent-manifest-object

### エージェントのプロビジョニング

Agents Toolkitのメニューから「LIFECYCLE」の「Provision」をクリックします。
![](/images/ms365-agent-toolkit-poc/2025-10-28-22-14-39.png)

以下のメッセージが表示されます。
Microsoft 365 Agents Toolkitで「Provision」操作を行うには、特定の権限を持つMicrosoft 365アカウントが必要です。アカウントを持っている場合は「Sign In」、持っていない場合はSandboxアカウントを作成しましょう。
![](/images/ms365-agent-toolkit-poc/2025-10-28-22-14-57.png)

以下のようになっていれば作成完了です。
![](/images/ms365-agent-toolkit-poc/2025-10-28-22-21-26.png)

### エージェントのテスト
https://m365.cloud.microsoft/chat の Copilot アプリケーションに移動します。

エージェントリストにある、作成した 宣言型エージェント「アイデアブラッシュアップ＆企画書作成エージェント」 を選択します。
![](/images/ms365-agent-toolkit-poc/2025-10-28-22-23-32.png)

このように表示されます。
下に表示されているのは、conversation_starters で定義した会話のきっかけとなる例文ですね。
![](/images/ms365-agent-toolkit-poc/2025-10-28-22-24-25.png)

こんな感じです。動作していますね。まだGPT4系なので、GPT-5系が利用可能になるとよいですね。
![](/images/ms365-agent-toolkit-poc/2025-10-28-22-27-59.png)

# まとめ
今回は、Microsoft 365 Agents Toolkit の使い方を知るために、Actionを持たないシンプルな Declarative Agent を作成してみました。
これであれば、Copilot画面から作成するのとできることは同じです。

次回以降では、Azure Functions などの API と連携する Action を持つエージェントや、JavaScript/TypeScriptでロジックを記述できる Imperative Agent の作成なども試してみたいと思います。

# 参考

https://learn.microsoft.com/en-us/microsoft-365/developer/overview-m365-agents-toolkit

https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/agents-toolkit-fundamentals

https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/build-environments

https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/tools-prerequisites