---
title: "Explorerでの検索は終わり！！ GPT4oで社内文書を活かすんやで！！！ (なごあず/すきやねんAzure7月)"
emoji: "📋"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "OpenAI", "GPT-4o", "RAG", "CosmosDB"]
published: false
---

# はじめに
2024年7月20日のなごあずの集い#2、2024年7月26日のすきやねんAzureのイベントに登壇しました。
https://75az.connpass.com/event/322194/
https://micug.jp/event/%e3%81%99%e3%81%8d%e3%82%84%e3%81%ad%e3%82%93-azure-%e3%83%81%e3%83%a3%e3%83%83%e3%83%88%e3%81%af%e9%a3%bd%e3%81%8d%e3%81%9f%e3%82%84%e3%82%8d%ef%bc%9f%e3%80%80aoai-%e3%81%ae%e3%81%84%e3%82%8d/

タイトルは
「Explorerでの検索は終り！！GPT4oで社内文書を活かすんやで！！！～Build の最新機能を使った RAG 構築～」
です。

:::message 
スライドはSpeakerDeckにアップしています。
:::
https://speakerdeck.com/nomhiro/gpt4odeshe-nei-wen-shu-wohuo-kasou-sukiyanenazure7yue-deng-tan-zi-liao?slide=54

この記事では、スライドの内容をもとに、ポイントとなる部分を紹介します。

# RAGとは？
生成AIだけでも、チャットコミュニケーション、学習済み知識を使った質問回答、コード生成、翻訳など、活用できるシーンが多々あります。
従来のAIは、機械学習を専門とするエンジニアが扱えるものでしたが、生成AIはAPIを呼べば使えるため、利用する敷居が低くなり、アプリ開発者も扱えるようになったことが大きな特徴だと言えます。
生成AIからの出力は、学習済みの知識から生成されます。インターネット上の情報を使って学習されています。そのため、**社内ドキュメントなどの情報は学習されていないため、社内ドキュメントに関する情報は生成AIからは回答できません。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-19-26-11.png)

生成AIが学習していないことを回答させる方法は2つあります。
- ファインチューニング（追加学習）
- RAG（Retrieval Augmented Generation）
この記事では、RAGについて紹介します。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-19-47-15.png)

RAGの仕組み概要です。
1. ユーザがチャット内容をアプリに送信します。
2. アプリは、社内文書が格納されているDBに、ユーザからのチャットに関連する情報を検索します。
3. 生成AIは、ユーザからのチャットに対し検索結果をもとに回答を生成します。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-19-48-10.png)

# RAGに関連するMicrosoft Build 2024の新サービス/新機能

Microsoft Build 2024にて、RAGに関わるサービスアップデートがいくつかありました。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-19-58-17.png)

## Azure OpenAI のアップデート
Azure OpenAIには、**GPT-4o**モデルが追加されました。
※その後7月にはGPT-4o miniも追加されましたね。スピード感がすごい...
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-19-59-31.png)

## Azure Cosmos DB のアップデート
Azure Cosmos DBには、ベクトル検索機能がPreviewされました。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-20-02-27.png)

:::details ベクトル検索とは
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-20-03-27.png)
:::

## Azure Functionsのアップデート
Azure Functionsには、**Flex従量課金プラン**がPreviewしたのが1つと、
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-20-03-59.png)

OpenAI拡張機能がPreviewしたのがもう1つです。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-20-06-14.png)

# サービスアップデートをもとにしたRAGアーキテクチャ
上記で紹介したサービスアップデートをもとに、RAGアーキテクチャを構築すると、以下のようになります。
- **Azure FunctionsのOpenAI拡張機能を使ってCosmosDBとAzureOpenAIと連携します。**
- **Azure Cosmos DBに検索用ドキュメントを格納し、ベクトル検索機能を使って検索します。**
- **Azure OpenAIのGPT-4oを使って回答を生成します。** 速度が期待できますね。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-20-11-01.png)

# RAGチャットアプリのデモ

対象のドキュメントは、すきやねんAzureのイベントページです。
![](/images/sukiyanen_june_rag_func_ext_openai_gpt4o/2024-08-16-20-56-12.png)

「7月のすきやねんAzureでは何が学べそう？」というチャットを想定しています。

このアーキテクチャで構築したチャットアプリケーションのデモ動画です。デモの流れは以下です。
- CosmosDBにドキュメントが登録されていない状態でチャットをしてみる。→GPT-4oは7月のすきやねんAzureの内容は学習していない。かつ検索されないため回答できない。
- CosmosDBにドキュメントを登録する。
- チャットをしてみる。→CosmosDBに登録されたドキュメントが検索され、回答が得られる。
- チャット履歴をDownloadする。

https://youtu.be/NJFp1DGKQc0

# まとめ
Build2024 で発表されたアップデートされたサービスにより、RAGの仕組みの選択肢が増えました。
- Functions OpenAI拡張機能がPreview
- Cosmos DB for NoSQLでのベクトル検索がPreview
- Auzre OpenAIのGPT-4oモデルがGA

CosmosDBのベクトル検索を使うことで、コスト効率よくRAGを構築できるようになりました。
FunctionsのOpenAI拡張機能を使うと、少ない実装量でOpenAIのAssistants機能を使い、チャットアプリケーションを実装できます。

参考として、本デモに対する実装時間は、4時間程度でした。


# おわりに
なごあず、すきやねんAzureはオフラインのイベントです。
今どきはオンラインイベントが多いですが、オフラインイベントですと、来てくださった方々と直に交流して生の声をお聞きできるので、非常に良い経験でした！！
またお世話になります。