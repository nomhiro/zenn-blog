---
title: "NLWebサーバーをローカルで動かそう！"
emoji: "🖥️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["nlweb", "microsoft", "ai", "llm"]
published: false
---

# はじめに
以前のブログで、NLWebについての概要を解説しました。
https://zenn.dev/nomhiro/articles/what-is-nlweb-2025-ms-build

:::message
NLWebとは、ウェブサイトに自然言語での対話型インターフェースを実装するためのオープンプロトコルとツール群。
ユーザーがチャット形式でウェブサイト内の情報を直接問い合わせできるようになります。
- 自然言語APIの統一性: 人間とAIエージェントの両方が利用可能。
- 構造化データの活用: Schema.orgやRSSを活用して簡単に対話型インターフェースを構築。
- マルチプラットフォーム対応: Windows、MacOS、Linuxなどで動作。
- 多様なLLMとデータベース対応: OpenAI、Azure AI Search、Qdrantなどをサポート。
:::

このブログでは、ローカル環境でNLWebサーバを立ち上げ、実際に動作を確認してみましょう。

# NLWebサーバーをローカルで動かそう！🚀

## 前提条件
- **Python 3.10以上**がローカルにインストールされていること
- Azure OpenAI に **gpt-4.1, gpt-4.1-mini, text-embedding-3-small** のモデルがデプロイされていること。
  - ![](/images/poc-nlweb-local-20250524/2025-05-24-17-43-37.png)


## 1. コードのダウンロード

まず、NLWebのリポジトリをクローンします。

```sh
git clone https://github.com/microsoft/NLWeb
cd NLWeb
```

## 2. Python仮想環境の作成と有効化

次に、Pythonの仮想環境を作成して、有効化します。これにより、プロジェクト専用の環境で必要なパッケージが管理できます。

```sh
python -m venv myenv
myenv\Scripts\activate
```

## 3. 依存関係のインストール

NLWebの`code`フォルダに移動し、依存ライブラリのインストールを行います。この手順で、ローカルのベクトルデータベース要求も含めたすべての必要なパッケージが自動的にインストールされます。

```sh
cd code
pip install -r requirements.txt
```

## 4. 設定ファイルの準備

#### 4-1. .envファイルの作成

`.env.template`ファイルをコピーして新しい`.env`ファイルを作成します。  
ここでは、使用する**LLMエンドポイントのAPIキー**を設定します。ローカルのQdrantデータベースの変数はすでに設定済みです。

```sh
cp .env.template .env
```

以下の環境変数を設定します。
```
AZURE_OPENAI_ENDPOINT="Azure OpenAI の API エンドポイント"
AZURE_OPENAI_API_KEY="Azure OpenAI の API キー"

QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY="<OPTIONAL>"
```

※ 必要に応じて、`.env`ファイル内のAPIキーなどをお使いの環境に合わせて編集してください。

#### 4-2. 設定ファイルの更新

`code/config`フォルダ内の3つの設定ファイルを更新します。これらのファイルで、使用するプロバイダーを自分の環境に合わせる必要があります。

- **config_llm.yaml**  
  - preferred_providerを、LLMプロバイダーに合わせて更新しましょう。デフォルトは「Azure OpenAI」になっています。 
  - 利用するモデル（例：4.1、4.1-mini）もここで変更します。※NLWebとしては4.1や4.1-miniの想定で作られているようです。

:::details config_llm.yaml
```yaml
preferred_provider: azure_openai

providers:
  inception:
    api_key_env: INCEPTION_API_KEY
    api_endpoint_env: INCEPTION_ENDPOINT
    models:
      high: mercury-small
      low: mercury-small

  openai:
    api_key_env: OPENAI_API_KEY
    api_endpoint_env: OPENAI_ENDPOINT
    models:
      high: gpt-4.1
      low: gpt-4.1-mini

  anthropic:
    api_key_env: ANTHROPIC_API_KEY
    models:
      high: claude-3-5-sonnet-20241022
      low: claude-3-haiku-20240307

  gemini:
    api_key_env: GCP_PROJECT
    models:
      high: chat-bison@001
      low: chat-bison-lite@001

  azure_openai:
    api_key_env: AZURE_OPENAI_API_KEY
    api_endpoint_env: AZURE_OPENAI_ENDPOINT
    api_version_env: "2024-12-01-preview"
    models:
      high: gpt-4.1
      low: gpt-4.1-mini

  llama_azure:
    api_key_env: LLAMA_AZURE_API_KEY
    api_endpoint_env: LLAMA_AZURE_ENDPOINT
    api_version_env: "2024-12-01-preview"
    models:
      high: llama-2-70b
      low: llama-2-13b

  deepseek_azure:
    api_key_env: DEEPSEEK_AZURE_API_KEY
    api_endpoint_env: DEEPSEEK_AZURE_ENDPOINT
    api_version_env: "2024-12-01-preview"
    models:
      high: deepseek-coder-33b
      low: deepseek-coder-7b

      
  snowflake:
    api_key_env: SNOWFLAKE_PAT
    api_endpoint_env: SNOWFLAKE_ACCOUNT_URL
    api_version_env: "2024-12-01"
    models:
      high: claude-3-5-sonnet
      low: llama3.1-8b
```
:::

- **config_embedding.yaml**  
  - 最上行を、希望する埋め込み（embedding）プロバイダーに更新します。デフォルトは「Azure OpenAI」で、モデルは`text-embedding-3-small`となっています。

:::details config_embedding.yaml
```yaml
preferred_provider: azure_openai

providers:
  openai:
    api_key_env: OPENAI_API_KEY
    api_endpoint_env: OPENAI_ENDPOINT
    model: text-embedding-3-small

  gemini:
    api_key_env: GCP_PROJECT
    model: GCP_EMBEDDING_MODEL

  azure_openai:
    api_key_env: AZURE_OPENAI_API_KEY
    api_endpoint_env: AZURE_OPENAI_ENDPOINT
    api_version_env: "2024-10-21"  # Specific API version for embeddings
    model: text-embedding-3-small

  snowflake:
    api_key_env: SNOWFLAKE_PAT
    api_endpoint_env: SNOWFLAKE_ACCOUNT_URL
    api_version_env: "2024-10-01"
    model: snowflake-arctic-embed-m-v1.5
```
:::

- **config_retrieval.yaml**  
  - こちらは、ローカル環境で動かすため、「qdrant_local」に変更します。
  （デフォルトはAzure AI Searchになっています）

:::details config_retrieval.yaml
```yaml
preferred_endpoint: qdrant_local

endpoints:
  azure_ai_search:
    api_key_env: AZURE_VECTOR_SEARCH_API_KEY
    api_endpoint_env: AZURE_VECTOR_SEARCH_ENDPOINT
    index_name: embeddings1536
    db_type: azure_ai_search
    name: NLWeb_Crawl

  # Option 1: Local file-based Qdrant storage
  qdrant_local:
    # Use local file-based storage with a specific path
    database_path: "../data/db"
    # Set the collection name to use
    index_name: nlweb_collection
    # Specify the database type
    db_type: qdrant
    
  qdrant_url:
    api_endpoint_env: QDRANT_URL
    api_key_env: QDRANT_API_KEY
    index_name: nlweb_collection
    db_type: qdrant

  snowflake_cortex_search_1:
    api_key_env: SNOWFLAKE_PAT
    api_endpoint_env: SNOWFLAKE_ACCOUNT_URL
    index_name: SNOWFLAKE_CORTEX_SEARCH_SERVICE
    db_type: snowflake_cortex_search
```
:::

## 5. ベクトルデータベースへのデータロード

次に、ローカルのベクトルデータベースにサンプルデータを読み込み、テストできるようにします。以下はRSSフィードを使用した例です。  
※ 複数のRSSフィードを読み込むと、複数の「サイト」を横断して検索が可能になります。特定のサイトに検索範囲を限定する場合は`config_nlweb.yaml`で設定します。

**今回は、Azureの更新情報のサイトのRSSを使います。**
https://azure.microsoft.com/ja-jp/updates/

```sh
python -m tools.db_load https://www.microsoft.com/releasecommunications/api/v2/azure/rss azure-update
```

:::details 実行結果
```bash
(myenv) PS C:\Users\user001\Documents\poc-nlweb-local-20250524\NLWeb\code> python -m tools.db_load https://www.microsoft.com/releasecommunications/api/v2/azure/rss azure-update
Logger embedding_wrapper writing to: logs\embedding_wrapper.log at level ERROR
Logger azure_search_client writing to: logs\azure_search_client.log at level ERROR
Logger milvus_client writing to: logs\milvus_client.log at level ERROR
Logger qdrant_client writing to: logs\qdrant_client.log at level ERROR
Logger retriever writing to: logs\retriever.log at level ERROR
Fetching content from URL: https://www.microsoft.com/releasecommunications/api/v2/azure/rss
Fetching content from URL: https://www.microsoft.com/releasecommunications/api/v2/azure/rss 
Saved URL content to temporary file: C:\Users\user01\AppData\Local\Temp\tmpohubzupg.xml (type: rss)
Detected file type: rss, contains embeddings: No
Computing embeddings for file...
Loading data from C:\Users\user01\AppData\Local\Temp\tmpohubzupg.xml (resolved to C:\Users\user01\AppData\Local\Temp\tmpohubzupg.xml) for site azure-update using database endpoint 'qdrant_local'
Detected file type: rss
Using embedding provider: azure_openai, model: text-embedding-3-small
Processing as RSS feed...
Processing RSS/Atom feed: C:\Users\user01\AppData\Local\Temp\tmpohubzupg.xml
Processed 200 episodes from RSS/Atom feed
Computing embeddings for batch of 100 texts
Logger azure_oai_embedding writing to: logs\azure_oai_embedding.log at level ERROR
Uploading batch 1 of 2 (100 documents)
Successfully uploaded batch 1
Processed 100/200 documents
Computing embeddings for batch of 100 texts
Uploading batch 2 of 2 (100 documents)
Successfully uploaded batch 2
Processed 200/200 documents
Loading completed. Added 200 documents to the database.
Saved file with embeddings to ../data/json_with_embeddings\tmpohubzupg.xml
Cleaned up temporary file: C:\Users\user01\AppData\Local\Temp\tmpohubzupg.xml
```
:::

## 6. NLWebサーバーの起動

準備が整ったら、NLWebサーバーを起動します。  
`code`フォルダ内で以下のコマンドを実行してください。

```sh
python app-file.py
```

---

## 7. 動作確認

サーバーが正常に起動したら、ブラウザで以下のURLにアクセスしてください。
![](/images/poc-nlweb-local-20250524/2025-05-24-17-55-02.png)

```
http://localhost:8000/
```

シンプルな検索インターフェースが表示され、正常に動作するはずです。  
![](/images/poc-nlweb-local-20250524/2025-05-24-17-55-48.png)

![alt text](/images/poc-nlweb-local-20250524/NLWeb-Answer-Local.gif)

また、いくつか異なるUIが用意されています。
- http://localhost:8000/static/debug.html
  - デバッグ用のページ
- http://localhost:8000/static/nlwebsearch.html
  - 結果をリスト形式で返すモードに特化したページ
- http://localhost:8000/static/mcp_test.html
  - MCPサーバとしての振る舞い（RequestとResponse）が確認できます。

※上記以外のhtmlファイルは、GitHubリポジトリで用意されているテストデータに特化して動作検証するためのページです。

#### debug.html
以下の設定をしたうえで、動作を確認できます。
- **Site**: 複数サイト全体を参照して回答を生成するか、特定のサイトのみのデータを参照するか
- **Mode**: list, summarize, generateのいずれかを選択します。

**summarize**で動作させてみます。データのlist表示の上に、要約情報が追加されましたね。
![alt text](/images/poc-nlweb-local-20250524/NLWeb-Answer-Local-Debug-Summarize.gif)

NLWebが保持しているRSSフィードの情報を確認できます。
Azure更新情報のRSSから取得したAzureサービスアップデート情報がリスト形式で格納されていることがわかります。

:::details デバッグ情報(Json)
```json
{
  "0": [
    {
      "url": "https://azure.microsoft.com/updates?id=494654",
      "name": "[Launched] Generally Available: Azure AI Foundry Agent Service ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 90,
      "description": "This podcast episode announces the general availability of the Azure AI Foundry Agent Service, detailing its capabilities such as supporting multi-agent workflows and enabling developers to build scalable AI agents. It provides a recent update directly related to Azure AI Foundry Service.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: Azure AI Foundry Agent Service ",
        "description": "Azure AI Foundry Agent Service is now generally available,

empowering developers to design, deploy, and scale enterprise-grade AI agents.

It supports multi-agent workflows, allowing specialized agents to handle

complex tasks, accelerate decisions, and boo",
        "datePublished": "Thu, 22 May 2025 16:00:23 Z",
        "url": "https://azure.microsoft.com/updates?id=494654",
        "identifier": "494654",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "1": [
    {
      "url": "https://azure.microsoft.com/updates?id=492104",
      "name": "[In preview] Public Preview: Azure Container Apps serverless GPUs now support Azure AI Foundry models ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode provides an update on Azure Container Apps serverless GPUs now supporting Azure AI Foundry models in public preview, which is a significant development related to Azure AI Foundry Service.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[In preview] Public Preview: Azure Container Apps serverless GPUs now support Azure AI Foundry models ",
        "description": "Azure

Container Apps serverless GPUs now support Azure AI Foundry models in public

preview. Azure AI Foundry Models have two deployment options - serverless APIs

and managed compute. Azure Container Apps serverless GPU offers a balanced

deployment option ",
        "datePublished": "Wed, 21 May 2025 03:30:39 Z",
        "url": "https://azure.microsoft.com/updates?id=492104",
        "identifier": "492104",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "2": [
    {
      "url": "https://azure.microsoft.com/updates?id=491980",
      "name": "[Launched] Generally Available: Import from Azure AI Foundry to Azure API Management’s AI Gateway ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode announces the general availability of a new feature in Azure AI Foundry that allows importing model endpoints directly into Azure API Management’s AI Gateway. It provides an update on Azure AI Foundry services, which is directly related to the topic.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: Import from Azure AI Foundry to Azure API Management’s AI Gateway ",
        "description": "Announcing

the general availability of importing model endpoints from Azure AI Foundry

directly into Azure API Management’s AI Gateway. This capability simplifies

onboarding of large language model (LLM) APIs by enabling seamless integration

through the A",
        "datePublished": "Fri, 23 May 2025 15:00:30 Z",
        "url": "https://azure.microsoft.com/updates?id=491980",
        "identifier": "491980",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "3": [
    {
      "url": "https://azure.microsoft.com/updates?id=493829",
      "name": "[Launched] Generally Available: Azure Functions integration with Azure AI Foundry Agent Service",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode announces the general availability of Azure Functions integration with Azure AI Foundry Agent Service, highlighting a significant update that enables building intelligent, event-driven applications. It provides timely and relevant information about new capabilities and enhancements related to Azure AI Foundry Service.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: Azure Functions integration with Azure AI Foundry Agent Service",
        "description": "Azure Functions integration with AI Foundry Agent service is now generally available. Integrating Azure Functions with AI Foundry Agent service enables you to build intelligent, event-driven applications that are scalable, secure, and cost-efficient. Azur",
        "datePublished": "Wed, 21 May 2025 03:30:39 Z",
        "url": "https://azure.microsoft.com/updates?id=493829",
        "identifier": "493829",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "4": [
    {
      "url": "https://azure.microsoft.com/updates?id=491247",
      "name": "[Launched] Generally Available: Azure Cosmos DB integration in Azure AI Agent Service ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode announces the general availability of Azure Cosmos DB integration within the Azure AI Foundry service, highlighting a significant update that enables AI apps and agents to utilize data from Azure Cosmos DB. It provides important information about new capabilities in Azure AI Foundry.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: Azure Cosmos DB integration in Azure AI Agent Service ",
        "description": "When designing and customizing AI apps and agents, you can now use the data stored in your Azure Cosmos DB accounts to power AI solutions built in Azure AI Foundry.  Azure Cosmos DB is the first Azure database able to power Azure AI Foundry agents and mod",
        "datePublished": "Mon, 19 May 2025 17:15:23 Z",
        "url": "https://azure.microsoft.com/updates?id=491247",
        "identifier": "491247",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "5": [
    {
      "url": "https://azure.microsoft.com/updates?id=490296",
      "name": "[In preview] Public Preview: Azure Databricks Azure AI Foundry Connector",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode introduces the public preview of the Azure Databricks Azure AI Foundry Connector, enabling seamless integration of AI agents with real-time data processing in Azure AI Foundry. It provides a direct update on new features related to Azure AI Foundry Service.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[In preview] Public Preview: Azure Databricks Azure AI Foundry Connector",
        "description": "You can now easily create AI agents in Azure AI Foundry with Azure Databricks data. Using the new Azure Databricks Azure AI Foundry connector, you can:   Connect Azure AI Foundry agents with Azure Databricks for real-time data processing.    Build and dep",
        "datePublished": "Mon, 19 May 2025 17:45:02 Z",
        "url": "https://azure.microsoft.com/updates?id=490296",
        "identifier": "490296",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "6": [
    {
      "url": "https://azure.microsoft.com/updates?id=494663",
      "name": "[Launched] Generally Available: New fine-tuning capabilities in Azure AI Foundry  ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode announces the general availability of new fine-tuning capabilities in Azure AI Foundry, including Reinforcement Fine-Tuning with the o4-mini model and Global Training across multiple Azure regions, providing important update information about Azure AI Foundry.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: New fine-tuning capabilities in Azure AI Foundry  ",
        "description": "Azure AI Foundry supports Reinforcement Fine-Tuning (RFT) with the o4-mini model in Azure OpenAI, enabling adaptive learning for context-aware applications. Alongside RFT, we introduced Global Training, allowing fine-tuning from 12+ Azure regions at reduc",
        "datePublished": "Thu, 22 May 2025 16:00:23 Z",
        "url": "https://azure.microsoft.com/updates?id=494663",
        "identifier": "494663",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "7": [
    {
      "url": "https://azure.microsoft.com/updates?id=494248",
      "name": "[In preview] Public Preview: Foundry Local for on-device AI",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 85,
      "description": "This podcast episode provides a public preview update on Foundry Local, a component of Azure AI Foundry Service that enables running AI models and tools directly on devices like Windows 11 and MacOS. It covers new features such as model inferencing, agents as a service, and a model playground, which are key aspects of the Azure AI Foundry ecosystem.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[In preview] Public Preview: Foundry Local for on-device AI",
        "description": "Foundry Local makes it easy to run AI models, tools and agents directly on-device, whether Windows 11 or MacOS . Foundry Local includes model inferencing, models, agents as a service, and model playground for fast and efficient local Al development. This ",
        "datePublished": "Tue, 20 May 2025 00:00:01 Z",
        "url": "https://azure.microsoft.com/updates?id=494248",
        "identifier": "494248",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "8": [
    {
      "url": "https://azure.microsoft.com/updates?id=491985",
      "name": "[Launched] Generally Available: Support for AWS Bedrock API in AI Gateway Capabilities in Azure API Management ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 70,
      "description": "This podcast episode discusses the integration of AWS Bedrock API support within Azure API Management's AI Gateway, which is part of Azure's AI service updates. Although it focuses on AWS Bedrock API support rather than Azure AI Foundry Service specifically, it is still relevant as it highlights recent advancements in Azure's AI capabilities and management features.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: Support for AWS Bedrock API in AI Gateway Capabilities in Azure API Management ",
        "description": "Announcing

expanded support for AWS Bedrock model endpoints across all Generative AI

policies in Azure API Management’s AI Gateway. This release enables you to

apply advanced management and optimization features such as Token Limit Policy,

Token Metric Po",
        "datePublished": "Fri, 23 May 2025 15:00:30 Z",
        "url": "https://azure.microsoft.com/updates?id=491985",
        "identifier": "491985",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "9": [
    {
      "url": "https://azure.microsoft.com/updates?id=491364",
      "name": "[In preview] Public Preview: Smarter Troubleshooting in Azure Monitor with AI-powered Investigation ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 70,
      "description": "This podcast episode discusses AI-powered troubleshooting features in Azure Monitor, which is part of Azure's AI capabilities. Although it is not specifically about Azure AI Foundry Service, it provides relevant insights into AI enhancements within Azure services.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[In preview] Public Preview: Smarter Troubleshooting in Azure Monitor with AI-powered Investigation ",
        "description": "These capabilities enhance your troubleshooting experience and streamline diagnosing and resolving health degradation of your application and infrastructure. AI-powered Investigations enable fast troubleshooting, diagnosing and resolving problems efficien",
        "datePublished": "Tue, 20 May 2025 16:45:48 Z",
        "url": "https://azure.microsoft.com/updates?id=491364",
        "identifier": "491364",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ],
  "10": [
    {
      "url": "https://azure.microsoft.com/updates?id=492589",
      "name": "[Launched] Generally Available: Natural Language App Code Generation ",
      "site": "azure-update",
      "siteUrl": "azure-update",
      "score": 70,
      "description": "This podcast episode discusses a new update related to Azure's AI capabilities, specifically focusing on natural language app code generation, which is part of Azure's AI services. Although it does not explicitly mention Azure AI Foundry Service, it provides relevant information about recent Azure AI developments that could be related or beneficial.",
      "schema_object": {
        "@type": "PodcastEpisode",
        "name": "[Launched] Generally Available: Natural Language App Code Generation ",
        "description": "In this new update, we are making it easier than ever for developers to get started creating their AI application with Azure. We are expanding the capabilities beyond the templates we offer out of the box, now giving the developers the option to describe ",
        "datePublished": "Wed, 21 May 2025 17:30:45 Z",
        "url": "https://azure.microsoft.com/updates?id=492589",
        "identifier": "492589",
        "partOf": {
          "@type": "PodcastSeries",
          "name": "Azure service updates",
          "description": "Azure service updates",
          "url": "https://www.microsoft.com/releasecommunications/api/v2/Azure/rss"
        }
      }
    },
    {}
  ]
}
```
:::

#### MCP.html
NLWebがMCPサーバとしてどのように振舞っているのか（どのようなクエリに対してどのようなMCPサーバからのレスポンスを返すのか）を確認できます。

![](/images/poc-nlweb-local-20250524/2025-05-24-23-29-51.png)

---

## まとめ

今回の手順では、NLWebのローカル環境でのPoC手順を紹介しました。以下のステップを通して、
1. **リポジトリのクローン＆仮想環境の構築**
2. **依存ライブラリのインストール＆環境設定**
3. **サンプルデータのデータベースへのロード**
4. **NLWebサーバーの起動と動作確認**

と進めることで、NLWebの基本機能と動作確認ができます。  
シンプルな手順で実行可能ですので、ぜひ試してみてください。  

次は、NlWebの中身がどのような仕組みで動いているかを深掘ろうと思います。