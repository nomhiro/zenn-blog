---
title: "Azure Functions の HTTPトリガータイムアウト 230s を回避する"
emoji: "🕰️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# はじめに

# PoC🚀

用意するものはこれらです。
- Azure Functions のPythonコード
- Azure Functions リソース

### Azure Functions のコード
以下のコードは、HTTP トリガーを受け取り、1秒から500秒のランダムな時間スリープする関数です。
```python
import azure.functions as func
import logging
import random
import time

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    # 1秒から500秒のランダムな時間を生成
    sleep_time = random.randint(1, 500)
    logging.info(f'Sleeping for {sleep_time} seconds.')

    start_time = time.time()
    elapsed_time = 0

    # スリープと10秒おきの経過時間ログ出力
    while elapsed_time < sleep_time:
        time.sleep(10)
        elapsed_time = time.time() - start_time
        logging.info(f'Elapsed time: {int(elapsed_time)} seconds')

        if elapsed_time + 10 > sleep_time:
            time.sleep(sleep_time - elapsed_time)
            elapsed_time = sleep_time
            logging.info(f'Elapsed time: {int(elapsed_time)} seconds')

    return func.HttpResponse(f'Slept for {sleep_time} seconds.', status_code=200)
```

### Azure Functions リソース作成
それでは、Azure Functions リソースを作成します。

Flex Consumption プランを選択して、作成します。
![](/images/azure-function-avoid-timeout/2025-02-20-22-16-28.png)

必要な情報を入力して、
![](/images/azure-function-avoid-timeout/2025-02-20-22-25-08.png)

作成します。
![](/images/azure-function-avoid-timeout/2025-02-20-22-26-38.png)

Done🚀
![](/images/azure-function-avoid-timeout/2025-02-20-22-28-43.png)


## タイムアウトの確認
まずは、以下のコードで、Azure Functions のデフォルトのタイムアウト時間を確認します。
```python
import requests

def call_azure_function():
    url = 'https://func-poc-timeout-test.azurewebsites.net/api/http_trigger'  # Azure FunctionのエンドポイントURL
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f'Response: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Error calling Azure Function: {e}')

if __name__ == '__main__':
    call_azure_function()
```

103sであれば、問題なくレスポンスが返ってきます。
![](/images/azure-function-avoid-timeout/2025-02-20-23-05-18.png)

次に、472sスリープした場合、Functions（のロードバランサー）からタイムアウトエラーが返ってきます。
![](/images/azure-function-avoid-timeout/2025-02-20-23-10-46.png)

ちなみに、Azure Functionsとしては230sを超えて動き続けてますね
![](/images/azure-function-avoid-timeout/2025-02-20-23-11-24.png)

## セッション維持のためのポーリング
Azure Functions の HTTP トリガーは、デフォルトで230秒のタイムアウトが設定されています。このタイムアウト時間を超える処理を行う場合、タイムアウトエラーが発生します。このような場合、セッション維持のためにポーリングを行うことで、タイムアウトエラーを回避することができます。

```python
import requests
from requests.exceptions import RequestException, Timeout

def call_azure_function():
    url = 'https://func-poc-timeout-test.azurewebsites.net/api/http_trigger'  # Azure FunctionのエンドポイントURL
    session = requests.Session()
    retries = 5  # 再試行回数
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=100)  # タイムアウトを設定
            response.raise_for_status()
            print(f'Response: {response.text}')
            break
        except Timeout:
            print(f'Timeout occurred. Retrying {attempt + 1} of {retries}...')
        except RequestException as e:
            print(f'Error calling Azure Function: {e}')
            break
    else:
        print(f'Failed to get a response after {retries} attempts.')

if __name__ == '__main__':
    call_azure_function()
```🧑‍🏫