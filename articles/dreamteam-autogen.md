---
title: "マルチエージェントアプリケーション「Dream Team」を調べて使ってみる"
emoji: "🧑‍🤝‍🧑"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "LLM", "Microsoft", "agent", "DreamTeam"]
published: true
---

# はじめに
2024年半ばから現在にかけて、生成AI周辺の  トレンドはエージェント化とそれらエージェントを組み合わせたマルチエージェントによる課題解決が主流となりつつあります。
※ここでのエージェントとは、特定の専門領域や専門タスクに特化していることとします。
複数のエージェントを組み合わせることで、1つのエージェントでは解決できない、もしくは精度が出ない課題が解決できるようになります。課題を解決するための複数のステップを、専門的なエージェントが実行します。

マルチエージェントフレームワークはいくつか出てきております。主要なものはこれらです。
### AutoGen
https://github.com/microsoft/autogen
自律的に動作する、または人間と協力して作業するマルチエージェントAIアプリケーションを作成するための包括的なフレームワークです。

::: details AutoGenの特長
- **フレームワーク**：AIエージェントを作成するための構造化された環境を提供し、特にマルチエージェントのワークフローに最適です。
- **開発者ツール**：AutoGen Studio（ノーコードGUI）やAutoGen Bench（ベンチマークスイート）などが含まれます。
- **アプリケーション**：様々なドメインでの応用が可能です。
:::

::: details 設計の特徴
- **レイヤードデザイン**：各レイヤーは明確に分かれ、それぞれが下位レイヤーの上に構築されています。これにより、高レベルのAPIから低レベルのコンポーネントまで、さまざまな抽象レベルでフレームワークを使用可能です。
- **Core API**：メッセージの受け渡し、イベント駆動エージェント、ローカルおよび分散ランタイムを実装し、.NETやPythonをサポートします。
- **AgentChat API**：プロトタイピング向けのシンプルで直感的なAPIです。
- **Extensions API**：拡張機能を提供し、コード実行や特定のLLMクライアントの実装をサポートします。
:::

::: details エコシステムのサポート
- **AutoGen Studio**：ノーコードGUIで、マルチエージェントアプリケーションの作成・プロトタイプ化が可能です。
- **AutoGen Bench**：エージェントのパフォーマンスを評価するためのベンチマークスイートです。
:::

### Magentic One
様々なドメインにおけるオープンエンドのウェブやファイルベースのタスクを解決するための汎用的なマルチエージェントシステムです。
Matsumoto-san のこちらの記事で、詳細でかつ他のフレームワークとの比較もされています。
https://zenn.dev/chips0711/articles/47ae142e51511b#%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97

### TinyTroupe
実際の人間をLLMで模擬したシミュレーションツールです。🤠🤓🥸🧐とあるように、さまざまな人格を模擬するイメージです。
特定の性格、興味、目標を持つ人々のシミュレーションを可能にする実験的な Python ライブラリです。
以前のこちらの記事で紹介していますのでご参考にしてください。
https://zenn.dev/nomhiro/articles/try-tinytroupe


# Dream Team
https://github.com/Azure-Samples/dream-team
https://techcommunity.microsoft.com/blog/Azure-AI-Services-blog/build-your-dream-team-with-autogen/4157961
さて、これらのようなマルチエージェントフレームワークがあるなかで、**Dream Team は、AutoGen及びMagenticOneをもとに開発された、マルチエージェントアプリケーション**です。マルチエージェントフレームワークのテストやデプロイも含まれています。

**主な機能**:
- **高度なマルチエージェントフレームワーク**：人気のあるAutogen（35Kスター）とMagentic Oneに基づいたソリューション。
- **使いやすいUI**：Streamlitを利用したデータアプリの構築と共有が簡単。
- **シングルラインデプロイ**：ローカル開発環境からAzureへの迅速なデプロイを実現するシングルラインコード - `azd up`。
- **セキュアなコード実行**：Azureコンテナアプリを使用して、強力な分離環境でのコードまたはアプリケーションの迅速な実行。
- **マネージドアイデンティティ**：開発者がこれらの資格情報を管理する必要を排除。
- **オブザーバビリティ＆デバッグ**：エージェントの相互作用とワークフローを追跡、トレース、デバッグするための組み込み機能とツール、PromptFlowトレースを含む。


# 早速使ってみましょう！🚀

## 前提条件
- Azure Developer CLIをインストール。
  - https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?tabs=winget-windows%2Cbrew-mac%2Cscript-linux&pivots=os-windows
- Azureサブスクリプションへのアクセスを確認。
- Dockerをインストールし、ログイン状態にする（`docker login -u "username" -p "password"`）。
- Pythonバージョン >= 3.10, < 3.13をインストール。
- ローカル実行のためにUVをインストール（オプション）
  - https://github.com/astral-sh/uv?tab=readme-ov-file#installation

詳細は、[AutoGenのGitHubリポジトリ](https://github.com/nomhiro/dream-team)をご覧ください。


## Azureにデプロイ

GitリポジトリをCloneします。
※ここではForkしたリポジトリ
```bash
git clone https://github.com/nomhiro/dream-team.git
```

azdコマンドでAzureアカウントにログインします。
```bash
azd auth login
```

azdコマンドでAzureリソースとアプリをデプロイします。
```bash
azd up
```
上記で解説したアーキテクチャの通り、以下のリソースがデプロイされます。
```bash
(✓) Done: Resource group: rg-dream-team-poc (5.054s)
(✓) Done: Log Analytics workspace: log-fyta4qfus3vki (24.256s)
(✓) Done: Key Vault: kv-fyta4qfus3vki (23.441s)
(✓) Done: Container Registry: crfyta4qfus3vki (27.056s)
(✓) Done: Application Insights: appi-fyta4qfus3vki (31.059s)
(✓) Done: Portal dashboard: dash-fyta4qfus3vki (2.784s)
(✓) Done: Container Apps Environment: cae-fyta4qfus3vki (1m44.921s)
(✓) Done: Azure OpenAI: dream (24.044s)
(✓) Done: Azure AI Services Model Deployment: dream/gpt-4o (763ms)
(✓) Done: Azure AI Services Model Deployment: dream/gpt-4o-mini (1.404s)
(✓) Done: Container App: src (38.033s)
```
![](/images/dreamteam-autogen/2025-02-06-22-18-30.png)


## ローカルで実行

GitリポジトリをCloneします。
※ここではForkしたリポジトリ
```bash
git clone https://github.com/nomhiro/dream-team.git
```

srcフォルダに移動します。
```bash
cd dream-team/src
```

Pythonの仮想環境を作成します。
```bash
uv venv
```

Pythonの仮想環境をアクティベートします。
```bash
.venv\Scripts\activate
```

Pythonモジュールをインストールします。
```bash
uv sync
playwright install --with-deps chromium
```

Azureにデプロイしたリソースの情報で設定を更新します。
```bash
azd env get-values > .env
```
以下の情報が.envファイルに保存されます。
```bash
AZURE_CONTAINER_REGISTRY_ENDPOINT="Azure Container Registryのエンドポイント"
AZURE_ENV_NAME="Azure Container Apps Environmentの名前"
AZURE_KEY_VAULT_ENDPOINT="Azure Key Vaultのエンドポイント"
AZURE_KEY_VAULT_NAME="Azure Key Vaultの名前"
AZURE_LOCATION="Azureリージョン"
AZURE_OPENAI_ENDPOINT="Azure OpenAIのエンドポイント"
AZURE_SUBSCRIPTION_ID="AzureサブスクリプションID"
POOL_MANAGEMENT_ENDPOINT="Azure Container Apps Environmentのエンドポイント"
SERVICE_SRC_IMAGE_NAME="Azure Container Registryのイメージ名"
SERVICE_SRC_RESOURCE_EXISTS="Azure Container Apps Environmentのリソースが存在するかどうか"

アプリケーションを起動します。
```bash
streamlit run app.py
```

### 動作させてみましょう！！！
FileSurfer、WebSurfer、Coder、Executorの複数のエージェントが使われるようなシーンを考えてみます。
**私のローカルPC内ののフォルダに保管されている自作アプリケーションに対し、似たプロダクトが世の中に存在するのかを聞いてみましょう。**
※自作アプリは、短編小説を作成するのをアシスタントするアプリケーションです。
```txt
C:\Users\xxxxxxx\Documents\story_creation_support
このフォルダ内のWebアプリケーションを把握して、世の中に似たような仕組みがあるのかを教えてください。
```
![](/images/dreamteam-autogen/2025-02-07-00-23-48.png)

まず、Orchestratorがメッセージに対して計画を立てました。以下の内容は日本語で要約した内容です。
```md
### チーム編成
- Coder: 言語スキル、Pythonスキル、Linuxコマンドラインスキルを持つ汎用AIアシスタント。
- Executor: Pythonスクリプトを実行するコンピュータターミナル（提供される sh コードブロック内で）。 
- FileSurfer: ローカルファイルを処理するエージェント。 
- WebSurfer: Webブラウザにアクセスできるアシスタント。ウェブ検索の実行、ページの開封、コンテンツの操作（リンククリック、ビューポートのスクロール、フォームフィールドの入力など）ができます。ページのロードに時間がかかる場合には、ページのロードを待つためにスリープさせることもできます。

### ファクトシート
1. 確認済み事実
  - リクエストはWindowsファイルシステム上のフォルダC:\Users\AdmUser\Documents\story_creation_supportから発信されています。 フォルダには「Webアプリケーション」が含まれていると指定されています。 リクエストの内容は: フォルダ内のWebアプリケーションの理解。 世界中に似たようなシステムがあるかの評価。
2. 調べるべき事実
  - フォルダの特定の内容を調べてWebアプリケーションを理解するには、そのフォルダへのローカルアクセスが必要です。 世界中に似たようなシステムがあるかどうかは、Webアプリケーションの機能、目的、および設計によります。調査には技術文書、学術論文、業界ツール、またはアプリケーションの機能に関連するウェブサイトの検索が含まれます。可能な情報源は次の通りです： GitHubリポジトリ（オープンソースまたは類似のツール用）。 ソフトウェア比較ウェブサイト（例：G2、Capterra、SaaSWorthy）。 テックブログおよびフォーラム（例：Stack Overflow、Dev.to）。 アプリケーションまたはその一部が特許で保護されている場合、知的財産レジストリまたは特許を確認することが関係する可能性があります。
3. 導き出すべき事実
  - Webアプリケーションの目的、設計、および機能を理解するためには、指定されたフォルダ内のファイル（例：コードベース、関連文書）を分析する必要があります。 「似たようなシステム」の判断は、重要な特徴や目的を特定し、それらを他の既知のシステムにマッピングすることに関わります。
4. 推測
  - フォルダ名は、Webアプリケーションがストーリーテリング、ライティング、またはコンテンツ作成の支援を目的としている可能性があることを示唆しています。このため、プロット生成、キャラクター開発、または共同ライティングなどの機能が含まれる可能性があります。 アプリケーションのファイルが存在する場合、それらの構造（例：HTML、JavaScript、ReactやAngularなどのフレームワーク、Node.jsやDjangoなどのバックエンド技術）に手がかりがあるかもしれません。含まれているフレームワークやライブラリは、その目的を示すかもしれません。 リクエストが類似システムの存在を求めていることから、このWebアプリケーションが革新的なアプローチを取っているか、ストーリーテリングやウェブベースのアプリケーションの広範な文脈でニッチなニーズを満たそうとしている可能性が高い

### 計画
- Step 1: 指定されたフォルダ内のWebアプリケーションを理解する
  - FileSurferを割り当てる:
    - フォルダ .C:\Users\AdmUser\Documents\story_creation_support に移動する
    - フォルダの内容（例：コード、ドキュメント、ファイル）をリストおよび探索して、Webアプリケーションの目的、構造、機能を特定する
    - ソースコードがある場合、使用されているプログラミング言語やフレームワークを特定する（例：HTML、JavaScript、Pythonなど）
    - README、メタデータ、またはアプリケーションを説明する他の説明ファイルがないか確認する
- Step 2: 世界中の類似システムを調査する
  - WebSurferを割り当てる:
    - Step 1からの洞察（例：主要機能、目的、アプリケーションのカテゴリー）に基づいて、類似システムを特定するためにウェブ検索を実行する
    - GitHubリポジトリ、ソフトウェア比較ウェブサイト（例：G2、Capterra）、テックブログ、またはフォーラムでアプリケーションの機能に一致するプロジェクトやツールを検索する
    - 詳細な分析のために注目すべき比較および事例をまとめる
- Step 3: 発見を統合する
  - Coderを割り当てる:
    - FileSurferとWebSurferからの出力を分析して、Webアプリケーションの包括的な理解を形成する
    - フォルダのWebアプリケーションと既存システムとの間の類似点または独自の特徴を要約する
    - 類似ツールが存在するかどうか、そしてこのアプリケーションがどのように比較または差別化されるかに焦点を当てて、発見の簡潔なレポートを準備する

```

::: details 元の英語はこちら
We are working to address the following user request:

C:\Users\AdmUser\Documents\story_creation_support このフォルダ内のWebアプリケーションを把握して、世の中に似たような仕組みがあるのかを教えてください。

To answer this request we have assembled the following team:

Coder: A helpful and general-purpose AI assistant that has strong language skills, Python skills, and Linux command line skills. Executor: A computer terminal that performs no other action than running Python scripts (provided to it quoted in sh code blocks). FileSurfer: An agent that can handle local files. WebSurfer: A helpful assistant with access to a web browser. Ask them to perform web searches, open pages, and interact with content (e.g., clicking links, scrolling the viewport, etc., filling in form fields, etc.). It can also summarize the entire page, or answer questions based on the content of the page. It can also be asked to sleep and wait for pages to load, in cases where the pages seem to be taking a while to load.python code blocks), or sh shell scripts (provided to it quoted in

Here is an initial fact sheet to consider:

1. GIVEN OR VERIFIED FACTS
The request originates from a folder located on a Windows file system: .C:\Users\AdmUser\Documents\story_creation_support
The folder is specified to contain a "Webアプリケーション" (web application).
The request asks for:
An understanding of the web application within that folder.
An evaluation of whether similar systems exist in the world ("世の中に似たような仕組み").
1. FACTS TO LOOK UP
The specific contents of the folder would need to be examined in order to understand the web application. This would require local access to that folder.C:\Users\AdmUser\Documents\story_creation_support
Whether similar systems exist in the world would depend on the functionality, purpose, and design of the web application. Research could involve searching technical documents, academic papers, industry tools, or websites that relate to the application’s features. Possible sources:
GitHub repositories (for open-source or similar tools).
Software comparison websites (e.g., G2, Capterra, SaaSWorthy).
Tech blogs and forums (e.g., Stack Overflow, Dev.to).
If the web application or parts of it are proprietary, checking intellectual property registries or patents might be relevant.
1. FACTS TO DERIVE
The purpose, design, and functionality of the web application would need to be derived from analyzing the files in the specified folder (e.g., codebase, associated documentation).
The determination of "similar systems" would involve identifying key features or purpose and mapping those to other known systems.
1. EDUCATED GUESSES
The folder name suggests that the web application might be intended for assisting with storytelling, writing, or content creation. This could mean capabilities like plot generation, character development, or collaborative writing.story_creation_support
If the application's files are present, there might be clues in their structure (e.g., HTML, JavaScript, frameworks like React or Angular, or back-end technologies like Node.js, Django, etc.). Frameworks or libraries included could hint at its purpose.
Since the request specifies finding if similar systems exist, it is likely this web application is either novel in its approach or attempting to serve a niche need within the broader context of storytelling or web-based applications.
Here is the plan to follow as best as possible:

Plan to Address the Request
Step 1: Understand the Web Application in the Specified Folder
Assign FileSurfer:
Navigate to the folder .C:\Users\AdmUser\Documents\story_creation_support
List and explore the contents of the folder (e.g., code, documentation, files) to determine the purpose, structure, and functionality of the web application.
If there is source code, identify the programming language or frameworks used (e.g., HTML, JavaScript, Python, etc.).
Check for any README, metadata, or other descriptive files that explain the application.
Step 2: Research Similar Systems in the World
Assign WebSurfer:
Based on the insights from Step 1 (e.g., key features, purpose, or category of the application), perform web searches to identify similar systems.
Search GitHub repositories, software comparison websites (e.g., G2, Capterra), tech blogs, or forums for projects or tools that align with the application’s functionality.
Compile notable comparisons and examples for further analysis.
Step 3: Synthesize Findings
Assign Coder:
Analyze the outputs from FileSurfer and WebSurfer to form a comprehensive understanding of the web application.
Summarize the similarities or unique characteristics between the folder’s web application and existing systems.
Prepare a brief report on findings, focusing on whether similar tools exist and how this application might compare or differentiate itself.
Notes:
Executor: No immediate need for executing scripts unless the web application must be run/tested locally as part of the analysis. FileSurfer can flag this if necessary.
This workflow can be iterative if the functionality of the web application is complex or requires deeper exploration for comparable systems.
:::

その後、以下のように会話が続いていきます。
OrchestratorがFileSurferに対し、フォルダの内容をリストアップする指示をして、FileSurferがフォルダ内の構造やファイルを提示しています。
![](/images/dreamteam-autogen/2025-02-06-23-55-59.png)

PowerPointの内容は、スライドごとにテキストで提示していますね。
![](/images/dreamteam-autogen/2025-02-06-23-57-08.png)

![](/images/dreamteam-autogen/2025-02-06-23-57-50.png)

Webアプリのフロント実装を深堀しています。
![](/images/dreamteam-autogen/2025-02-06-23-58-20.png)

**アプリの内容が把握できたので、アプリ内容をもとにWebSerfureが似たアプリケーションが世の中にあるのかどうかを検索しに行きます。**
![](/images/dreamteam-autogen/2025-02-06-23-58-42.png)

![](/images/dreamteam-autogen/2025-02-06-23-59-45.png)

**検索結果をもとに、Coderが指定したアプリと検索できた類似ツールを比較します。**
![](/images/dreamteam-autogen/2025-02-07-00-00-18.png)

![](/images/dreamteam-autogen/2025-02-07-00-00-41.png)

![](/images/dreamteam-autogen/2025-02-07-00-00-55.png)

**結論が得られたため、最後にOrchestratorが要約します。**
世の中の類似ツールの説明と、類似ツールとの差分をまとめてくれていますね
![](/images/dreamteam-autogen/2025-02-07-00-01-18.png)


**最後に、最終的なまとめがなされ、報告書のダウンロードが可能です。**
![](/images/dreamteam-autogen/2025-02-07-00-05-17.png)


# まとめ
Dream Teamでは、Magentic-Oneで提供されている、「Coder」「Executor」「FileSurfer」「WebSurfer」のエージェントがデフォルトで用意されていて、さらに自前のエージェントをシステムメッセージとエージェントの説明を定義することで追加できます。さらに、RAG用AgentもAISearchのIndexを指定することで自由に追加できることが特長です。
※AISearchのIndexのフィールドには、"parent_id", "chunk_id", "chunk","text_vector"のフィールドが必要です。
今回の例では、ローカルPC内のフォルダをエージェントが探して解析し、類似ツールの有無をWeb検索のエージェントが実行するというシナリオを実行しました。オーケストレーターが最初に計画を立て、各エージェントの実行とオーケストレーターのNextAction決めが動的に行われるため、非常に柔軟な仕組みだと感じました。
また、Azureにデプロイした仕組みはContainerAppsで動作するため、従量課金プランにしておけば使った分だけの請求になるのも良いですね。