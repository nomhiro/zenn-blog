---
title: "OpenAPI Generator 「Kiota」を使ってみよう"
emoji: "🪡"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["openapi", "kiota", "generator", "semantickernel", "microsoft"]
published: false
---

![](/images/intro-openapi-kiota/2024-11-08-21-16-46.png)

# 背景
生成AIを扱う中で、Tools（FunctionCalling）で世の中で公開されているAPI群を呼び出し実行すること仕組みを考えていくと、パラメータや仕様が異なる各APIをAPIごとに人手で実装するのが非効率だなと思いました。
そのため、APIをどう公開しそれをAIがどう呼び出すかを調べると、OpenAPIという思想があることがわかりました。

# OpenAPIとは
私が解釈したOpenAPIの利用イメージはこちらです。（間違ってたりしたら教えてください）
- APIを公開する人は、APIとともにAPIの仕様（ymlファイル）を公開します
- APIを利用する人は、公開されているAPIの使用（ymlファイル）をもとに、Kiotaなどのコード生成ツールを使うことで、APIを呼び出すためのソースコードを生成できます
![OpenAPIのイメージ](/images/intro-openapi-kiota/2024-11-08-21-21-58.png)

# Kiotaの概要

Kiotaのコード生成プロセスの概念はこちらです。
1. OpenAPIのYamlもしくはJsonを定義
2. URLスペースツリー
   - PathItemsのリストをもとにリソース構造を作成。フィルターすることで使用されるリソースのみを含めることでライブラリサイズを小さく最適化できる
3. コードモデル
   - OpenAPI PathItems が分析され、対応する言語に依存しないコード モデルが作成される
4. 言語によるコードモデルの絞り込み
   - 生成されたソースコードに必要な言語フレームワークの依存関係をインポートする
5. ソースファイルの生成
   - コードモデルを取得し、それを言語固有のテキストに変換する
   - CodeElement階層を走査し、具体的なLanguageWriter実装を適用すると、目的のソースコードが出力される

### 依存関係
- クライアントを生成または更新した後は、Kiotaの依存関係が info コマンドで推奨されるバージョンと一致していることを確認するべきだそうです
  - infoコマンド：https://learn.microsoft.com/ja-jp/openapi/kiota/using#language-information


# Pythonで使ってみる
使ってみないとわからないので、PythonでKiotaを使ってみます。

## 事前準備

- requirements.txtにkiotaのモジュールを追加し、"pip install -r requirements.txt"でインストールします。
```
microsoft-kiota-abstractions
microsoft-kiota-http
microsoft-kiota-serialization-json
microsoft-kiota-serialization-text
microsoft-kiota-serialization-form
microsoft-kiota-serialization-multipart
```

## APIクライアント生成

以下のRestAPIのモック用のAPIサイトで試してみます。
https://jsonplaceholder.typicode.com/

1. ymlファイルにOpenAPIのAPI定義します
```yml
openapi: '3.0.2'
info:
  title: JSONPlaceholder
  version: '1.0'
servers:
  - url: https://jsonplaceholder.typicode.com/

components:
  schemas:
    post:
      type: object
      properties:
        userId:
          type: integer
        id:
          type: integer
        title:
          type: string
        body:
          type: string
  parameters:
    post-id:
      name: post-id
      in: path
      description: 'key: id of post'
      required: true
      style: simple
      schema:
        type: integer

paths:
  /posts:
    get:
      description: Get posts
      parameters:
      - name: userId
        in: query
        description: Filter results by user ID
        required: false
        style: form
        schema:
          type: integer
          maxItems: 1
      - name: title
        in: query
        description: Filter results by title
        required: false
        style: form
        schema:
          type: string
          maxItems: 1
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/post'
    post:
      description: 'Create post'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/post'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/post'
  /posts/{post-id}:
    get:
      description: 'Get post by ID'
      parameters:
      - $ref: '#/components/parameters/post-id'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/post'
    patch:
      description: 'Update post'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/post'
      parameters:
      - $ref: '#/components/parameters/post-id'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/post'
    delete:
      description: 'Delete post'
      parameters:
      - $ref: '#/components/parameters/post-id'
      responses:
        '200':
          description: OK
```

2. Kiotaを使い、APIを呼び出すためのAPIクライアントクラスを生成します

kiotaのコマンドラインツールで実行します。
```bash
kiota generate -l python -c PostsClient -n client -d ./posts-api.yml -o ./client
```
![](/images/intro-openapi-kiota/2024-11-05-15-37-09.png)

:::details VSCodeでの手順

まずVSCodeの拡張機能をインストールします
![](/images/intro-openapi-kiota/2024-11-02-19-26-05.png)

OpenAPI拡張機能から、「Add API Description」をクリック
![](/images/intro-openapi-kiota/2024-11-05-12-28-58.png)

「Browse Path」をクリックし、先ほど作成したymlファイルを選択
![](/images/intro-openapi-kiota/2024-11-05-12-33-07.png)

![](/images/intro-openapi-kiota/2024-11-05-12-39-52.png)

OpenAPI descriptionが生成されます
![](/images/intro-openapi-kiota/2024-11-05-12-46-33.png)

APIを選択して、クライアントクラスを生成しましょう
APIを「＋」で選択
![](/images/intro-openapi-kiota/2024-11-05-12-56-32.png)

選択したAPIがチェックマークになっていることを確認して、「Generate」
![](/images/intro-openapi-kiota/2024-11-05-12-59-34.png)

![](/images/intro-openapi-kiota/2024-11-05-13-00-04.png)

TestRestClient
![](/images/intro-openapi-kiota/2024-11-05-13-05-17.png)

TestRestApiSDK
![](/images/intro-openapi-kiota/2024-11-05-13-06-05.png)

![](/images/intro-openapi-kiota/2024-11-05-13-06-47.png)

Pythonを選ぶ
![](/images/intro-openapi-kiota/2024-11-05-13-07-51.png)

ファイルタブにて、生成されたファイルを確認します
生成されるのは、
- test_rest_client.py
- postsフォルダ
  - posts_request_builder.py
- modelsフォルダ
  - post.py
- .kiotaフォルダ

![](/images/intro-openapi-kiota/2024-11-05-13-08-24.png)
:::

:::message alert
VSCodeで生成したクライアントコードを使うと、以下エラーが発生しました。（なぜなのか、深追いできてません）
**Kiotaのコマンドラインツールで生成したクライアントコードを使うことをお勧めします。**

``` bash
Exception has occurred: Exception Content type application/json does not have a factory registered to be parsed File "/workspaces/OpenAPI/client/posts/posts_request_builder.py", line 44, in get return await self.request_adapter.send_collection_async(request_info, Post, None) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/workspaces/OpenAPI/main.py", line 26, in main all_posts = await client.posts.get() ^^^^^^^^^^^^^^^^^^^^^^^^ File "/workspaces/OpenAPI/main.py", line 59, in <module> asyncio.run(main()) Exception: Content type application/json does not have a factory registered to be parsed
```

:::

## 生成されたクライアントクラスを利用
生成されたクライアントクラスを利用し、APIを呼び出してみます。

```python
import asyncio
from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from client.posts_client import PostsClient
from client.models.post import Post

async def main():
    # Windowsでasyncioを使用する場合に必要な場合があります
    # 参照: https://stackoverflow.com/questions/63860576
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # APIは認証を必要としないため、匿名認証プロバイダーを使用します
    auth_provider = AnonymousAuthenticationProvider()
    # HTTPXベースの実装を使用してリクエストアダプターを作成します
    request_adapter = HttpxRequestAdapter(auth_provider)
    # APIクライアントを作成します
    client = PostsClient(request_adapter)

    # GET /posts
    all_posts = await client.posts.get()
    print(f"{len(all_posts)}件の投稿を取得しました。")

    # GET /posts/{id}
    specific_post_id = "5"
    specific_post = await client.posts.by_post_id(specific_post_id).get()
    print(f"投稿を取得しました - ID: {specific_post.id}, " +
          f"タイトル: {specific_post.title}, " +
          f"本文: {specific_post.body}")

    # POST /posts
    new_post = Post()
    new_post.user_id = 42
    new_post.title = "Kiota生成APIクライアントのテスト"
    new_post.body = "こんにちは、世界！"

    created_post = await client.posts.post(new_post)
    print(f"新しい投稿を作成しました - ID: {created_post.id}")

    # PATCH /posts/{id}
    update = Post()
    # タイトルのみ更新
    update.title = "更新されたタイトル"

    updated_post = await client.posts.by_post_id(specific_post_id).patch(update)
    print(f"投稿を更新しました - ID: {updated_post.id}, " +
          f"タイトル: {updated_post.title}, " +
          f"本文: {updated_post.body}")

    # DELETE /posts/{id}
    await client.posts.by_post_id(specific_post_id).delete()

# メイン関数を実行
asyncio.run(main())
```

実行結果はこちら
![](/images/intro-openapi-kiota/2024-11-05-15-49-33.png)


# まとめ

OpenAPIを使うことで、ymlファイルにAPI定義を記述するだけで、クライアントコードを生成できることが確認できました。
APIを開発するチームがOpenAPIの定義も一緒に公開することで、APIを利用するチームが簡単にクライアントコードを生成できるようになりそうです。

また、生成AIを活用した場合、SemanticKernelというAIオーケストレーション層のフレームワークでは、OpenAPIの定義を元に、APIのクライアントコードを生成するプラグインを提供しています。
https://learn.microsoft.com/ja-jp/semantic-kernel/concepts/plugins/adding-openapi-plugins?pivots=programming-language-csharp

今後どう活用されていくか、注視しておこうと思います。