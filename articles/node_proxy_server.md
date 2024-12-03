---
title: "nodeでプロキシーサーバを実装する"
emoji: "🪛"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["node", "proxy", "Azure", "OpenAI"]
published: false
---

# モチベーション

ある事情から、クライアント環境からAzureOpenAIにアクセスする際に、AzureOpenAIのFQDNを使ってアクセスできず、特定のドメイン名でアクセスする必要がありました。
ApplicationGatewayなどで対応することもできたかもしれませんが、暫定的な対応として、Node.jsでプロキシーサーバを実装してみました。

![](/images/node_proxy_server/2024-12-03-21-53-15.png)

# プロキシサーバの実装

## 実装コード

コード全体の流れ
1. HTTPサーバーを作成してリクエストを受信。
2. 受け取ったリクエストをパースして転送先を設定。
3. 転送先のホストにリクエストを転送。
4. 転送先からのレスポンスを受け取り、元のクライアントに返す。
5. エラーハンドリング。

プロキシサーバのNodejsのコードはこちらです。

```javascript
const http = require('http');
const https = require('https');
const url = require('url');

const proxy = http.createServer((req, res) => {
  console.log(`🚀Received request: ${req.method} ${req.url}`);

  const parsedUrl = url.parse(req.url);
  const targetUrl = parsedUrl.path;

  const options = {
    hostname: 'aoai-rag.openai.azure.com', // 転送先のホスト名
    port: 443, // 転送先のポート
    path: targetUrl,
    method: req.method,
    headers: req.headers,
    rejectUnauthorized: false // 証明書の検証をスキップ
  };
  console.log(` Proxying request to: ${options.hostname}${options.path}`);
  // headerのhostを変更
  options.headers.host = 'aoai-rag.openai.azure.com';
  console.log(` headers: ${JSON.stringify(options.headers)}`);
  
  const proxyReq = https.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });

    // 転送先からの応答をコンソールに出力
    proxyRes.on('data', (chunk) => {
      console.log(`Response chunk: ${chunk}`);
    });

    proxyRes.on('end', () => {
      console.log('Response ended.');
    });
  });

  req.pipe(proxyReq, { end: true });

  proxyReq.on('error', (err) => {
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Something went wrong.');
    console.error(err);
  });
});

proxy.listen(3000, () => {
  console.log('Proxy server is running on port 3000');
});
```

## 起動します

実装したコードで、プロキシサーバを起動します。

```bash
$ node proxy.js
```

![](/images/node_proxy_server/2024-12-03-22-43-38.png)

# 稼働確認しましょう！

## OpenAISDKを使ったクライアント側想定のコード

稼働確認は、PythonのOpenAI SDKを使って行います。

前提として、環境変数に以下の二つの値を設定しておきます。
- 通常ですと、AOAI_ENDPOINTに`https://aoai-rag.openai.azure.com`を設定しますが、プロキシサーバを経由させたいので、起動したプロキシサーバのエンドポイントを設定します。
- AOAI_KEYはAzureOpenAIのAPIキーです。
```bash
AOAI_ENDPOINT=http://localhost:3000
AOAI_KEY=AzureOpenAIのAPIキー
```

こちらがPythonのコードです。

```python
import os
from openai import AzureOpenAI

# 環境変数からエンドポイントとキーを取得
endpoint = os.getenv("AOAI_ENDPOINT")
key = os.getenv("AOAI_KEY")
print(endpoint, key)

# クライアントの初期化
client = AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version="2024-07-01-preview")

# チャットの実行
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "こんにちは、元気ですか？"}
    ]
)

# 応答の表示
print(response.choices[0].message.content)
```

## それではプロキシサーバ経由で実行🚀！！！

クライアント側想定のPythonコードの実行結果はこちらです。
![](/images/node_proxy_server/2024-12-03-22-48-33.png)

そして、プロキシサーバーのコンソールには、以下のようにリクエストとレスポンスが表示されています。
![](/images/node_proxy_server/2024-12-03-22-49-28.png)

プロキシサーバを経由してAzureOpenAIにアクセスできてますね🎉！！


# 参考
実装したコードはこちらのGitHubリポジトリにあります。
https://github.com/nomhiro/nodejs_proxy_openai