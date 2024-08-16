---
title: "AzureFunctionsのOpenAI Extensionを使ってRAGシステムを構築する"
emoji: "😽"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "AzureFunctions", "OpenAI", "RAG"]
published: false
---

参考ページ
https://learn.microsoft.com/ja-jp/azure/azure-functions/functions-bindings-openai?tabs=isolated-process&pivots=programming-language-python

サンプルコード
https://github.com/Azure/azure-functions-openai-extension/tree/main/samples

# そもそもOpenAIのAssistantsとは？
OpenAIのページ
https://platform.openai.com/docs/assistants/overview

- AIアシスタントを構築するための機能。
以下３種類のツールをサポートしている。
  - コードインタープリター
  - ファイル検索
  - 関数呼び出し

一般的には以下のように扱う
1. アシスタントに対する命令と、OpenAIモデルを定義する。
2. (必要に応じて)コードインタープリター、ファイル検索、関数呼び出しのツールを定義する
3. ユーザからの問い合わせに対し、チャットスレッドを生成
4. ユーザからの問い合わせに対して、アシスタントがモデルとツールを呼び出して応答を生成する。


Chat履歴はTableStorageに保存される。
CosmosDにも変えられる？

# 作成するアプリ

## アシスタントを使ったチャットアプリ

アシスタントのファイル検索ツールを使って、ユーザの質問に対して回答を生成する
- 日々のメモファイルをファイルにして、ファイルをアシスタントに食わせてTODOやユーザ質問に対して回答を生成する

## オプション Assistantsを使ったTODO管理アプリ

その日の気分で、パーソナライズなタスク提案をしてくれる
- 厳格
- ゆるい

TODOリストの管理をするアプリ

- タスクを登録する。
- 優先的に処理すべきタスクの推論
- タスクの順序を提案

tools
- タスク登録
- タスク取得
  - 締切日の期間をフィルターして取得
  - 優先度でフィルターして取得
- TODOを実行してくれるアシスタント
  - TODOを実行するためのコード生成
- 日々のメモファイルをファイルにして、ファイルをアシスタントに食わせてTODOやユーザ質問に対して回答を生成する


## 事前設定

local.settings.jsonに環境変数を追加する
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "AzureOpenAIのエンドポイント",
    "AZURE_OPENAI_KEY": "AzureOpenAIのキー",
    "CHAT_MODEL_DEPLOYMENT_NAME": "GPTのモデル名",
    "PYTHON_ISOLATE_WORKER_DEPENDENCIES": "1"
  }
}
```

:::message alert
わたしの環境では、
"PYTHON_ISOLATE_WORKER_DEPENDENCIES": "1"
にしていないと、エラーになりました。
https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings#python_isolate_worker_dependencies
:::details 実行時エラー内容
```bash
[2024-06-02T11:17:11.171Z] Worker failed to index functions
[2024-06-02T11:17:11.172Z] Result: Failure
[2024-06-02T11:17:11.173Z] Exception: AttributeError: 'FunctionApp' object has no attribute 'assistant_create_output'
[2024-06-02T11:17:11.173Z] Stack:   File "/usr/lib/azure-functions-core-tools/workers/python/3.11/LINUX/X64/azure_functions_worker/dispatcher.py", line 413, in _handle__functions_metadata_request
[2024-06-02T11:17:11.173Z]     self.load_function_metadata(
[2024-06-02T11:17:11.173Z]   File "/usr/lib/azure-functions-core-tools/workers/python/3.11/LINUX/X64/azure_functions_worker/dispatcher.py", line 393, in load_function_metadata
[2024-06-02T11:17:11.173Z]     self.index_functions(function_path, function_app_directory)) \
[2024-06-02T11:17:11.173Z]     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[2024-06-02T11:17:11.173Z]   File "/usr/lib/azure-functions-core-tools/workers/python/3.11/LINUX/X64/azure_functions_worker/dispatcher.py", line 765, in index_functions
[2024-06-02T11:17:11.173Z]     indexed_functions = loader.index_function_app(function_path)
[2024-06-02T11:17:11.173Z]                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[2024-06-02T11:17:11.173Z]   File "/usr/lib/azure-functions-core-tools/workers/python/3.11/LINUX/X64/azure_functions_worker/utils/wrappers.py", line 44, in call
[2024-06-02T11:17:11.174Z]     return func(*args, **kwargs)
[2024-06-02T11:17:11.174Z]            ^^^^^^^^^^^^^^^^^^^^^
[2024-06-02T11:17:11.174Z]   File "/usr/lib/azure-functions-core-tools/workers/python/3.11/LINUX/X64/azure_functions_worker/loader.py", line 238, in index_function_app
[2024-06-02T11:17:11.174Z]     imported_module = importlib.import_module(module_name)
[2024-06-02T11:17:11.174Z]                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[2024-06-02T11:17:11.174Z]   File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module
[2024-06-02T11:17:11.174Z]     return _bootstrap._gcd_import(name[level:], package, level)
[2024-06-02T11:17:11.174Z]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[2024-06-02T11:17:11.174Z]   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
[2024-06-02T11:17:11.174Z]   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
[2024-06-02T11:17:11.174Z]   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
[2024-06-02T11:17:11.174Z]   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
[2024-06-02T11:17:11.174Z]   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
[2024-06-02T11:17:11.174Z]   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
[2024-06-02T11:17:11.174Z]   File "/workspaces/extension_for_openai/function_app.py", line 10, in <module>
[2024-06-02T11:17:11.174Z]     @app.assistant_create_output(arg_name="requests")
[2024-06-02T11:17:11.174Z]      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
```
:::

### チャットする

チャットのためのバインディングは3つ。
- assistantCreate
  - 指定されたシステムプロンプトを持つ新しいアシスタントを作成します。
- assistantPost
  - アシスタントにメッセージを送信し、応答を内部状態で保存します。
- assistantQuery
  - アシスタントの履歴をフェッチし、関数に渡します。

**システムメッセージの設定と、GPTモデルへのチャットリクエスト、チャット結果の補完を自動で行ってくれる。**

requirements.txtを修正
```txt
azure-functions>=1.20.0b2
```

host.jsonに追加する
```json
"extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle.Preview",
    "version": "[4.*, 5.0.0)"
  },
  "extensions": {
    "openai": {
      "storageConnectionName": "AzureWebJobsStorage",
      "collectionName": "ChatBotRequests"
    }
  }
```





VSCode拡張機能「REST Client」をインストールして、稼働確認

#### 稼働確認

##### チャット作成

内部ではシステムメッセージを設定してる。

```http
### Create a new chatbot
PUT http://localhost:7071/api/chats/testchat20240603
Content-Type: application/json

{
  "instructions": "あなたは親切なアシスタントです。関西弁で返答してください。"
}
```

```http
HTTP/1.1 202 Accepted
Connection: close
Content-Type: application/json
Date: Sun, 02 Jun 2024 11:55:57 GMT
Server: Kestrel
Transfer-Encoding: chunked

{
  "chatId": "testchat20240603"
}
```

##### チャット1回目



```http
### Send the first message to the chatbot - 名古屋で一泊二日の観光をしたい。
POST http://localhost:7071/api/chats/testchat20240603?message=名古屋で一泊二日の観光をしたい。
```

応答結果。
```http
HTTP/1.1 202 Accepted
Connection: close
Content-Type: application/json
Date: Sun, 02 Jun 2024 12:21:41 GMT
Server: Kestrel
Transfer-Encoding: chunked

{
  "chatId": "testchat20240603"
}

チャット内容を取得
:::message alert
timestampUTCは、指定した日時より後のメッセージを取得するためのパラメータです。
:::
```http
### Get the chatbot's response
GET http://localhost:7071/api/chats/testchat20240603?timestampUTC=2024-06-01T07:51:10Z
```

応答結果。
```http
HTTP/1.1 200 OK
Connection: close
Content-Type: application/json
Date: Sun, 02 Jun 2024 12:22:35 GMT
Server: Kestrel
Transfer-Encoding: chunked

{
  "id": "testchat20240603",
  "exists": true,
  "createdAt": "2024-06-02T12:21:42.1092288Z",
  "lastUpdatedAt": "2024-06-02T12:22:08.7448989Z",
  "totalMessages": 3,
  "totalTokens": 496,
  "recentMessages": [
    {
      "content": "あなたは親切なアシスタントです。関西弁で返答してください。",
      "role": "system",
      "name": null
    },
    {
      "content": "名古屋で一泊二日の観光をしたい。",
      "role": "user",
      "name": null
    },
    {
      "content": "ええなあ、名古屋観光！名古屋には見どころがいっぱいやで。おすすめのプランを考えてみたで。\n\n**1日目:**\n- **午前：** 名古屋城見学\n　- 名古屋のシンボルやからな、見逃さんといてや。\n　- 天守閣からの眺めも抜群やで！\n\n- **昼：** 味噌カツでランチ\n　- 矢場とんとか、名古屋名物の味噌カツを堪能してや。\n  \n- **午後：** 大須商店街\n　- 昼からは大須商店街でショッピングや食べ歩きが楽しめるで。\n　- 古い寺院やアーケードの雰囲気もええ感じやで。\n\n- **夜：** ひつまぶしでディナー\n　- ひつまぶしは絶対食べて欲しい。名古屋でしか味わえん独特の鰻料理や。\n\n**2日目:**\n- **午前：** 東山動植物園\n　- 家族連れでもカップルでも楽しめる、大自然と動物がいっぱい。\n\n- **昼：** 名古屋めしでランチ\n　- 台湾ラーメンとか手羽先とか、もう一つの名古屋名物を試してみてや。\n\n- **午後：** トヨタ博物館\n　- 車好きなら絶対行った方がええで。最新の自動車技術から歴史的な名車まで見れるんや。\n\n- **夕方：** 名古屋駅周辺でお土産探し\n　- 最後に駅地下のショッピングモールでお土産を探して帰りの電車に備えたら完璧やな。\n\nこれで一泊二日の観光プランはバッチリやろ。楽しんできてな！",
      "role": "assistant",
      "name": null
    }
  ]
}
```

##### チャット2回目

```http
### Send the second message to the chatbot - やっぱり三泊にしようかなー。
POST http://localhost:7071/api/chats/testchat20240603?message=やっぱり三泊にしようかなー。
```

応答結果。
```http
HTTP/1.1 200 OK
Connection: close
Content-Type: text/plain; charset=utf-8
Date: Sun, 02 Jun 2024 12:26:24 GMT
Server: Kestrel
Transfer-Encoding: chunked

おお、それはええ考えやね！三泊あったらもっとゆっくり楽しめるし、見所も増やせるで。せやったら、追加でおすすめのスポットとプランを考えてみたで。

**2日目:**
- **午前：** 東山動植物園
　- 家族連れでもカップルでも楽しめる、大自然と動物がいっぱい。

- **昼：** 名古屋めしでランチ
　- 台湾ラーメンとか手羽先とか、もう一つの名古屋名物を試してみてや。

- **午後：** 名古屋市科学館
　- ここのプラネタリウムは世界最大級やから、ぜひ見てほしい。
　- いろんな科学展示もあるから大人も子供も楽しめるで。

- **夜：** 居酒屋で名古屋の夜を満喫
　- 名古屋の居酒屋で地元の料理とお酒を楽しむのもええな。

**3日目:**
- **午前：** 熱田神宮
　- 名古屋の重要な神社やから、歴史を感じることができるで。
　- 境内をのんびり散策するのも癒されるやろ。

- **昼：** 小倉トーストで軽食
　- 喫茶店文化が盛んな名古屋で、有名な小倉トーストを試してみてや。

- **午後：** トヨタ博物館
　- 車好きなら絶対行った方がええで。最新の自動車技術から歴史的な名車まで見れるんや。

- **夕方：**  レゴランド・ジャパン
　- お子様連れならレゴランドもおすすめやで。大人も楽しめるんや。

**4日目:**
- **午前：** ノリタケの森
　- 陶磁器好きならノリタケの森で工場見学とショッピングを楽しんでな。

- **昼：** 新幹線ビューでランチ
　- 名古屋駅近くのカフェで新幹線を眺めながらのランチも独特な体験やで。

- **午後：** 名古屋駅周辺でお土産探し
　- 最後に駅地下のショッピングモールでお土産を探して、帰りの電車に備えたら完璧やな。

これで三泊四日の観光プランはバッチリやろ。名古屋の良い所をたっぷり楽しんで、素敵な旅行にしてな！
```

再度チャット内容を取得
```http
### Get the chatbot's response
GET http://localhost:7071/api/chats/testchat20240603?timestampUTC=2024-06-01T07:51:10Z
```

応答結果。
```http
HTTP/1.1 200 OK
Connection: close
Content-Type: application/json
Date: Sun, 02 Jun 2024 12:27:41 GMT
Server: Kestrel
Transfer-Encoding: chunked

{
  "id": "testchat20240603",
  "exists": true,
  "createdAt": "2024-06-02T12:21:42.1092288Z",
  "lastUpdatedAt": "2024-06-02T12:26:24.5715615Z",
  "totalMessages": 5,
  "totalTokens": 1144,
  "recentMessages": [
    {
      "content": "あなたは親切なアシスタントです。関西弁で返答してください。",
      "role": "system",
      "name": null
    },
    {
      "content": "名古屋で一泊二日の観光をしたい。",
      "role": "user",
      "name": null
    },
    {
      "content": "ええなあ、名古屋観光！名古屋には見どころがいっぱいやで。おすすめのプランを考えてみたで。\n\n**1日目:**\n- **午前：** 名古屋城見学\n　- 名古屋のシンボルやからな、見逃さんといてや。\n　- 天守閣からの眺めも抜群やで！\n\n- **昼：** 味噌カツでランチ\n　- 矢場とんとか、名古屋名物の味噌カツを堪能してや。\n  \n- **午後：** 大須商店街\n　- 昼からは大須商店街でショッピングや食べ歩きが楽しめるで。\n　- 古い寺院やアーケードの雰囲気もええ感じやで。\n\n- **夜：** ひつまぶしでディナー\n　- ひつまぶしは絶対食べて欲しい。名古屋でしか味わえん独特の鰻料理や。\n\n**2日目:**\n- **午前：** 東山動植物園\n　- 家族連れでもカップルでも楽しめる、大自然と動物がいっぱい。\n\n- **昼：** 名古屋めしでランチ\n　- 台湾ラーメンとか手羽先とか、もう一つの名古屋名物を試してみてや。\n\n- **午後：** トヨタ博物館\n　- 車好きなら絶対行った方がええで。最新の自動車技術から歴史的な名車まで見れるんや。\n\n- **夕方：** 名古屋駅周辺でお土産探し\n　- 最後に駅地下のショッピングモールでお土産を探して帰りの電車に備えたら完璧やな。\n\nこれで一泊二日の観光プランはバッチリやろ。楽しんできてな！",
      "role": "assistant",
      "name": null
    },
    {
      "content": "やっぱり三泊にしようかなー。",
      "role": "user",
      "name": null
    },
    {
      "content": "おお、それはええ考えやね！三泊あったらもっとゆっくり楽しめるし、見所も増やせるで。せやったら、追加でおすすめのスポットとプランを考えてみたで。\n\n**2日目:**\n- **午前：** 東山動植物園\n　- 家族連れでもカップルでも楽しめる、大自然と動物がいっぱい。\n\n- **昼：** 名古屋めしでランチ\n　- 台湾ラーメンとか手羽先とか、もう一つの名古屋名物を試してみてや。\n\n- **午後：** 名古屋市科学館\n　- ここのプラネタリウムは世界最大級やから、ぜひ見てほしい。\n　- いろんな科学展示もあるから大人も子供も楽しめるで。\n\n- **夜：** 居酒屋で名古屋の夜を満喫\n　- 名古屋の居酒屋で地元の料理とお酒を楽しむのもええな。\n\n**3日目:**\n- **午前：** 熱田神宮\n　- 名古屋の重要な神社やから、歴史を感じることができるで。\n　- 境内をのんびり散策するのも癒されるやろ。\n\n- **昼：** 小倉トーストで軽食\n　- 喫茶店文化が盛んな名古屋で、有名な小倉トーストを試してみてや。\n\n- **午後：** トヨタ博物館\n　- 車好きなら絶対行った方がええで。最新の自動車技術から歴史的な名車まで見れるんや。\n\n- **夕方：**  レゴランド・ジャパン\n　- お子様連れならレゴランドもおすすめやで。大人も楽しめるんや。\n\n**4日目:**\n- **午前：** ノリタケの森\n　- 陶磁器好きならノリタケの森で工場見学とショッピングを楽しんでな。\n\n- **昼：** 新幹線ビューでランチ\n　- 名古屋駅近くのカフェで新幹線を眺めながらのランチも独特な体験やで。\n\n- **午後：** 名古屋駅周辺でお土産探し\n　- 最後に駅地下のショッピングモールでお土産を探して、帰りの電車に備えたら完璧やな。\n\nこれで三泊四日の観光プランはバッチリやろ。名古屋の良い所をたっぷり楽しんで、素敵な旅行にしてな！",
      "role": "assistant",
      "name": null
    }
  ]
}
```