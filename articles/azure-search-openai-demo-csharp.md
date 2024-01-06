---
title: "RAGを使用した.NET Chatサンプルアプリ"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "AISearch", "OpenAI", "RAG", "CSharp"]
published: false
---

# Microsoft提供のRAGを使用した.NET Chatサンプルアプリを試してみる

## 背景
- 社内でOpenAIのRAGを使ったチャットボットを作成するシーンが増えてきています。
- 以前はStreamlitを使ったPythonのサンプルアプリを紹介しましたが、
[OpenAIを簡単に検証するためにStreamlitを使う](https://zenn.dev/nomhiro/articles/streamlit-use-openai)
[StreamlitアプリをAzureのAppServiceで動かす](https://zenn.dev/nomhiro/articles/deploy-streamlit-to-appservice)
今回はMicrosoftが提供している.NETのサンプルアプリを紹介します。このサンプルアプリには、AzureAISearchを使ったRAGの検索機能が組み込まれているため、社内ドキュメントを用意するだけですぐにRAGが組み込まれたChatを試すことができます。

## 構成
- Microsoftドキュメントはこちらです。
[RAG を使用した .NET エンタープライズ チャット サンプルの概要](https://learn.microsoft.com/ja-jp/dotnet/azure/ai/get-started-app-chat-template?tabs=visual-studio-code)
- アーキテクチャはこのようになっています。
    ![](/images/azure-search-openai-demo-csharp/2023-12-31-17-53-14.png)
    1. このチャットアプリで提供されるWebアプリ
    2. ドキュメントを検索するためのサービス
        ※2023年11月にCognitiveSearch→AISearchに名前が変わっています。
    3. チャットと検索結果を組み合わせて推論する


## 実際に試してみる
Microsoftドキュメントの手順をベースに進めていきます。

### 前提条件
- Visual Studio Codeを使います。

### 開発環境を構築

1. 任意のディレクトリを作成
    ※ここでは「azure-search-openai-demo-csharp」
2. Azure Developer CLI を使用して Azure にサインインします。
    ※ブラウザで認証画面が表示されるため、Azureアカウントでサインインします。
    ```bash
    azd auth login
    ```
    ![azd auth login](/images/azure-search-openai-demo-csharp/2023-12-31-18-06-19.png)
3. Azure Developer CLI フォルダーを初期化します。
    ```bash
    azd init -t azure-search-openai-demo-csharp
    ```
    ![init project](/images/azure-search-openai-demo-csharp/2023-12-31-18-08-45.png)
4. [コマンド パレット] を開き、Dev Containers コマンドを検索し、[Dev Containers: コンテナーで再度開く (Reopen in Container)] を選択します。
    ![ReOpenContainer](/images/azure-search-openai-demo-csharp/2024-01-01-09-30-54.png)

### Azureにデプロイして実行する
- Azure Developer CLI コマンドを実行して、Azure リソースをプロビジョニングし、ソース コードをデプロイ
    ```bash
    azd up
    ```
    - サブスクリプションとリージョンを選択します。
      - リージョン：(US) East US (eastus)
    ![select subscription and resourceGroup](/images/azure-search-openai-demo-csharp/2024-01-01-09-44-12.png)

## まとめ