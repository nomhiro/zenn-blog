---
title: "2025年の振り返り"
emoji: "🌟"
type: "idea" # tech: 技術記事 / idea: アイデア
topics: ["2025", "2026", "Azure", "AI", "振り返り"]
published: false
---

![](/images/summary-2025/2025-12-31-22-06-47.png)

わたしの2025年を振り返りたいと思います。
技術ブログを書いたり技術コミュニティに参加しだしたのが2024年からでした。それを思えば、**ここ2年で技術活動がかなり活発に**なりました。

2024年から継続して、**月2本の技術ブログ**によるOutputと、**月1回以上のコミュニティ登壇**を意識しながら活動していました。
どのような内容であっても、技術の紹介はもちろんのこと、どのようなユースケースで使うのか？を意識しながらPoCを行っていました。
そのため、振り返ると、自然と以下のような流れが出来上がっていました。
1. 個人的に気になった内容をPoC
2. PoCした内容をブログで整理する
3. 登壇することで、より抽象化した知見をコミュニティに還元する


また、なるべく最新の情報をコミュニティに還元していくためにも、Microsoft Ignite直後の11月は3回登壇しました。

## 活動サマリー

| 種別 | 件数 |
|------|------|
| ブログ記事 | 27本 |
| 登壇 | 9回 |

登壇については、会社として参加したものを含めるとさらに増えますが、個人として技術コミュニティに参加したものをカウントしています。

---

## 注力していたテーマ

1. **MCP（Model Context Protocol）** - 7件
   - Azure Functions × MCP、Cosmos DB MCP、Neo4j MCP、SLM × MCPなど
   
2. **マルチエージェント/Agent Framework** - 6件
   - AutoGen、Dream Team、Agent Framework、Durable Task Schedulerとの組み合わせ

3. **Azure AI Foundry エコシステム** - 5件
   - Foundry Local、Browser Automation、Agent Service

4. **ローカルLLM/SLM活用** - 4件
   - phi-4、phi-4-mini、ハイブリッドAI構成

---

# 2025年の技術活動

## 1月

### 【ブログ】DurableFunctionsとAPIManagementを使ったAgentAPI管理による Agentic World を考える

https://zenn.dev/nomhiro/articles/agentic-world-api-management

専門家Agentとオーケストレーションの考え方を整理し、Durable Functionsによるワークフロー定義とAPI Managementによるエージェント管理について整理しました。

## 2月

### 【ブログ】【論文翻訳】認証された委任と認可されたAIエージェント

https://zenn.dev/nomhiro/articles/authorized-ai-agents

AIエージェントに対する認証認可アーキテクチャに関する論文を解説した記事です。OAuth 2.0とOpenID Connectをエージェント固有の認証情報で拡張するアプローチについて紹介しています。

### 【ブログ】マルチエージェントアプリケーション「Dream Team」を調べて使ってみる

https://zenn.dev/nomhiro/articles/dreamteam-autogen

AutoGen、Semantic Kernel、CrewAIなどのマルチエージェントフレームワークを比較し、Microsoftの「Dream Team」サンプルアプリケーションを実際に動かしてみたPoC記事です。

### 【ブログ】【OmniRAG】ベクトル検索とナレッジグラフによるRAG ~ Azure Cosmos AI Graph ~

https://zenn.dev/nomhiro/articles/cosmos-ai-graph-rag

ベクトル検索とナレッジグラフを組み合わせたRAG手法について、Azure Cosmos DBのグラフ機能を活用した実装を紹介しました。

## 3月

### 【ブログ】Vercel AI SDK で AIモデルごとのSDKに依存しないアプリを実装しよう！

https://zenn.dev/nomhiro/articles/poc-vercel-ai-sdk

複数のAIモデルを統一的に扱うVercel AI SDKの活用方法を、Next.jsとの連携を通じて解説しました。

### 【ブログ】【OCR革命！？】Mistral OCR で生成AIが理解できる構造化データにしよう🚀

https://zenn.dev/nomhiro/articles/poc-mistral-ocr

Mistral OCRを使って文書をMarkdown化し、RAGの精度向上につなげるOCR技術の活用方法を紹介しました。

### 【ブログ】Azure AI Agent を MCPサーバ で公開し、Vercel AI SDK を使ったアプリから実行しよう🚀

https://zenn.dev/nomhiro/articles/mcp-azure-ai-foundry-use-vercel-ai-sdk

MCPの基本概念とFunctionCallingとの違いを整理し、Azure AI AgentをMCPサーバとして公開する方法を解説しました。

## 4月

### 【ブログ】Azure CosmosDB MCPサーバ を使って、自然言語でデータ取得してみよう！

https://zenn.dev/nomhiro/articles/mcp-azure-cosmosdb

Cosmos DBのMCPサーバを構築し、自然言語でデータベースクエリを実行する方法を紹介しました。

## 5月

### 【ブログ】Next.js と Auth.js でWebアプリにGoogleアカウント認証と認可を実装しよう

https://zenn.dev/nomhiro/articles/nextjs-authjs-v5

Auth.js v5を使った認証実装について、Googleアカウントによるソーシャルログインの導入方法を解説しました。
これは、自分で運用しているWebアプリのプロダクトに使いたく、実際に導入した内容をまとめました。

### 【ブログ】Azure Container Apps を 仮想ネットワーク統合とプライベートエンドポイントで閉域化する

https://zenn.dev/nomhiro/articles/containerapps_private_network

Container Appsのネットワーク閉域化について、仮想ネットワーク統合とプライベートエンドポイントの設定方法を解説した記事です。

### 【ブログ】NLWebで広がる新たな対話型ウェブサイトの世界

https://zenn.dev/nomhiro/articles/what-is-nlweb-2025-ms-build

Microsoft Build 2025で発表された「NLWeb」について紹介した記事です。ウェブサイトにAIによる対話型インターフェースを実装するためのオープンプロトコルとツール群について解説しました。

### 【ブログ】NLWebサーバーをローカルで動かそう！

https://zenn.dev/nomhiro/articles/poc-nlweb-local-20250524

ローカル環境でNLWebサーバを立ち上げ、実際に動作をPoCした記事です。

### 【ブログ】【論文解説】ホンダの動的な知識更新を行うマルチエージェントAIシステム ~ワイガヤ~

https://zenn.dev/nomhiro/articles/honda-multi-agent-systems

ICLR 2025採択論文を解説した記事です。ホンダが開発した動的知識統合型マルチエージェントシステム「ワイガヤ」について紹介しました。

## 6月

### 【ブログ】AutoGen (0.6.1) の基本的な構成要素

https://zenn.dev/nomhiro/articles/autogen0-6-1-poc

複数のAIが協力して問題を解決するマルチエージェントシステムの実装について、AutoGen 0.6.1の基本コンポーネントを整理しました。

### 【ブログ】Neo4jのMCPでグラフデータベースに自然言語で問い合わせよう！！！

https://zenn.dev/nomhiro/articles/neo4j-mcp-person-knowledge

グラフデータベースNeo4jとMCPを連携し、自然言語でナレッジグラフに問い合わせるRAG実装をまとめました。

### 【登壇】AzureでMCPサーバ！！どう活用する？

https://75az.connpass.com/
https://www.docswell.com/s/shirokuma/Z6J1WW-75azu-20250621

- イベント: #75azu（なごあずの集い）
- 日程: 2025年6月21日
AzureでMCPサーバを作成する方法を紹介し、生成AIエージェントとツール連携についてお話しました。

## 7月

### 【ブログ】【phi-4】Foundry LocalでSLMを実行！！～ローカルPC内完結するためにSLM活用してみよう～

https://zenn.dev/nomhiro/articles/slm-foundry-local-poc-01

SLM（Small Language Model）をローカルで実行する方法について、Foundry LocalでPhi-4を動作させるPoCを紹介した記事です。

### 【登壇】チャットアプリ失敗談！製造業業務への生成AI導入

https://kinto-technologies.connpass.com/event/354960/ 
https://www.docswell.com/s/shirokuma/KEY2MN-chatapp-nagoyallmmeetup

- イベント: #名古屋LLMMeetUp
- 日程: 2025年7月23日

KINTOテクノロジーズが主催する名古屋LLM MeetUpで、製造業の業務に生成AIを導入しようとした際のチャットアプリ開発失敗談を共有しました。

## 8月

### 【ブログ】AutoGenの会話をWebアプリ（Streamlit）上に表示しよう！！

https://zenn.dev/nomhiro/articles/autogen-streamlit-chat-view

AutoGenマルチエージェントの会話をStreamlitで可視化し、非同期でエージェント間チャットをリアルタイム表示できるように実装しました。

### 【ブログ】StreamlitでMermaidのマインドマップを表示する

https://zenn.dev/nomhiro/articles/streamlit-mermaid-maindmap

Mermaid.jsを使ったマインドマップをStreamlitで表示する実装を紹介しました。

### 【ブログ】Mermaid.jsでクリック可能なマインドマップを実装する（Next.js）

https://zenn.dev/nomhiro/articles/mindmap-node-click-nextjs

Next.jsでMermaid.jsを活用し、インタラクティブなマインドマップを実装しました。

### 【ブログ】【SLM×MCP】SLM（phi-4-mini）からMCPを使ってツールを呼び出したい

https://zenn.dev/nomhiro/articles/slm-mcp-tool-call

ローカルSLMとMCPを連携させ、phi-4-miniからツールを呼び出す実装方法を紹介した記事です。

### 【ブログ】AI Foundry Browser Automation Tool で定常業務を自動化してみよう！

https://zenn.dev/nomhiro/articles/browser-automation-ai-foundry-poc

Azure AI FoundryのBrowser Automation機能（Preview）を使い、Playwrightを活用した自然言語でのブラウザ操作自動化を紹介しました。

### 【登壇】Azure AI Foundry Portal デモ

https://jazug.connpass.com/event/361970/
https://www.docswell.com/s/shirokuma/KN9N6W-aifoundryagentservice

- イベント: JAZUG×なんでもCopilot　夏休み特大号　#jaznancopa
- 日程: 2025年8月16日

ぺぺさんと共同で、Azure AI Foundry Portalのデモンストレーションを行いました。

## 9月

### 【ブログ】AzureFunctionsのMCPサーバで生成AIドリブンな一歩を踏み出そう！ ～ManagedIDアクセスを添えて～

https://zenn.dev/nomhiro/articles/azure-functions-mcp-managed-id

Azure FunctionsをMCPサーバーとして活用し、Managed Identityによるセキュアなアクセスを実現する方法をまとめました。

### 【登壇】生成AI最前線：最新トレンドと活用事例の紹介

https://no-maps.jp/program/tech/121500/

- イベント: NO MAPS 2025（札幌）
- 日程: 2025年9月15日

KINTOテクノロジーズの和田颯馬さんと共同登壇しました。社内チャットアプリを自分たちで作る意義について、クラウドアーキテクチャなどのシステム設計から開発で得た知見・文化的側面までおはなししました。

## 10月

### 【ブログ】【Agent Framework（Python）】クルマ提案エージェント ～Functions MCPも～

https://zenn.dev/nomhiro/articles/agent-framework-car-dealer-agent-poc

Microsoft Agent Frameworkを使ったエージェント実装について、Azure FunctionsのMCPサーバと連携したクルマ提案エージェントを作成した記事です。

### 【ブログ】Azure OpenAI 「gpt-realtime」 モデルとツール呼び出しを使った音声対話エージェント

https://zenn.dev/nomhiro/articles/poc-voice-live-api-ai-agent

WebRTCを活用したRealtime API実装について、音声対話中のFunction Callingを実現する方法を解説した記事です。
リアルタイムな音声対話を行いながら、裏ではFunctionCallingでツール呼び出しできるようにしました。さらに、音声から音声を直接生成するのでリアルタイム性が高いです。
RAGや外部APIアクセスによるActionを行いながら音声対話できるようになったことで、より高度な対話エージェントを作れるようになっています。

## 11月

### 【ブログ】【2025年11月】Microsoft Copilot Studio: エージェント設計・評価・拡張徹底ガイド

https://zenn.dev/nomhiro/articles/m365-copilot-studio-feature-20251108

Copilot Studioの最新機能を解説し、エージェント設計・評価の実践ガイドとしてまとめました。

### 【ブログ】Microsoft 365 Agents Toolkit ~入門~

https://zenn.dev/nomhiro/articles/ms365-agent-toolkit-poc

Microsoft 365 CopilotやTeamsで動作するエージェント開発について、Declarative Agentの作成方法を解説しました。

### 【登壇】AzureでのAIエージェントはここから！Azure Functions × AI

https://kinto-technologies.connpass.com/event/370357/
https://www.docswell.com/s/shirokuma/574PR2-AzureAIIAgentgnite2025

- イベント: #名古屋LLMMeetUp
- 日程: 2025年11月21日

KINTOテクノロジーズが主催する名古屋LLM MeetUpで、Azure Functionsを活用したAIエージェント構築についてお話しました。
この時は、その週にMicrosoft Ignite 2025で発表されたばかりの内容を前日や当日に盛り込み、Azureにおける最新のAzure AIエージェント開発手法を紹介しました。

### 【登壇】AzureでAIエージェント、さて何から始める？

https://yonayona.connpass.com/event/374591/
https://www.docswell.com/s/shirokuma/ZG27V8-YonaAz-20251127

- イベント: #YonaAz
- 日程: 2025年11月27日

PoC部の一員であるYuya-sanが主催するイベントで、Microsoft Igniteで発表する内容も織り込みながら、AzureでAIエージェントを始めるためのステップを紹介させていただきました。
https://x.com/yuyanz_

### 【登壇】リアルタイム音声モデルgpt-realtimeを使った音声対話ツール

https://jazug.connpass.com/event/368296/
https://www.docswell.com/s/shirokuma/K6EP2P-gpt-realtime-voice-agent

- イベント: #jazug_shizuoka（第3回 JAZUG Shizuoka）
- 日程: 2025年11月29日

10月にブログで紹介したgpt-realtimeモデルを使った音声対話エージェントについて、静岡のJAZUGコミュニティで発表しました。
初めてJAZUG Shizuokaに参加させていただきまして、静岡を大好きになりました。愛知県からも近いので、また参加させていただきます！

## 12月

### 【登壇】ローカルとクラウドLLMのハイブリッドAI活用 ~セキュリティとプライバシー保護の観点から~

https://75az.connpass.com/event/373754/
https://www.docswell.com/s/shirokuma/KPGDW7-2025-12-06-75azu-hybrid-ai

- イベント: #75azu（なごあずの集い#7）
- 日程: 2025年12月6日

ローカルLLM（SLM）での処理をMCPサーバで公開し、Azure OpenAIと組み合わせたハイブリッドAIアーキテクチャについて紹介しました。機密データをローカルで処理し、高度な推論のみクラウドで実行するセキュアな構成についてお話ししました。

### 【ブログ】ローカルとクラウドLLMのハイブリッドAI活用

https://zenn.dev/nomhiro/articles/hybrid-ai-local-azure-security

Azure PoC部 Advent Calendar 2025 8日目の記事です。Foundry Local（Phi-4-mini）とAzure OpenAIを組み合わせたハイブリッドAIアーキテクチャについて、機密データをローカルで処理し、高度な推論のみクラウドで実行するセキュアな構成を紹介しています。

### 【ブログ】Durable Task Scheduler と Agent Framework による可視化可能なマルチエージェントシステム

https://zenn.dev/nomhiro/articles/agent-framework-multi-agent-20251213

Azure PoC部 Advent Calendar 2025の記事です。Microsoft Agent FrameworkとDurable Task Schedulerを組み合わせた「事前承認会マルチエージェントチャット」を構築し、担当者の提案に対してCTO、CFO、事業部長といった役員エージェントが議論してフィードバックを返す仕組みを紹介しています。

### 【ブログ】【続編】ローカルとクラウドLLMのハイブリッドAI ~Queue Polling~

https://zenn.dev/nomhiro/articles/hybrid-ai-local-azure-security-using-queue

Azure PoC部 Advent Calendar 2025 21日目の記事です。MCP + Dev Tunnel方式の課題を解決するため、Azure Storage Queueを使用したポーリング方式を実装し、アウトバウンド接続のみでセキュアなクラウド・ローカル連携を実現する方法を紹介しています。

### 【登壇】ローカルとクラウド LLM のセキュアなハイブリッド構成（【続編】ローカルとクラウドLLMのハイブリッドAI ~Queue Polling~）

https://sukiyanenazure.connpass.com/event/375556/ 
https://www.docswell.com/s/shirokuma/K37X3V-hybrid-local-cloud-queue

- イベント: #すきやねんAzure  
- 日程: 2025年12月26日

JAZUG Shizuoka にてお話ししたローカルとクラウドLLMのハイブリッドAIをブラッシュアップし、Queue Polling方式を導入したセキュアな構成について紹介しました。
ハイブリッド利用のアーキテクチャとしてはこれが完成形に近いと思いますので、ぜひ参考にしていただき、様々なユースケースで活用していただければと思います。


---

# まとめ

2026年も、引き続き個人的興味と世の中へのユースケース/社会実装を意識しながら、よりワクワクする、楽しいと思える技術活動を続けていきたいと思います！
皆さま、2025年も大変お世話になりました。2026年もどうぞよろしくお願いいたします！