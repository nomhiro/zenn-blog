---
title: "OpenAIを簡単に検証するためにStreamlitを使う"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "OpenAI", "Streamlit", "Python"]
published: true
---

# OpenAIを簡単に検証するためにStreamlitでチャットする

## この記事を書いた背景

AzureOpenAIを利用してプロンプトやチャットを試したいときに、一般的にはAzureAIStudioのPlayGroundを利用すると思います。
PlayGroundはインターネットを経由したブラウザ接続で利用するため、場合によっては社内での利用が難しい場合があります。そのような場合は独自にチャットができるアプリを用意する必要があります。

## 紹介すること／紹介しないこと

StreamlitはPythonで簡単にWebアプリを作成できるフレームワークです。今回はStreamlitを利用して、OpenAIのチャットを簡単に試す方法を紹介します。

* 紹介すること
  * この記事では、**PC環境でStreamlitを起動する方法を紹介します。**
* 紹介しないこと
  * AzureサービスにStreamlitをデプロイする方法は紹介しません。別途書きます。

## 前提条件

* Python 3.12
* Docker環境（DevContainer利用）
  
## アプリの作成

実際にStreamlitを利用してアプリを作成してみます。

サンプルコードはこちらのリポジトリにあります。
[サンプルコード](https://github.com/hiroki-nomura/streamlit-chat-aoai)

### chat.pyファイルに以下のコードを記載します

:::message alert
※2023年11月のMicrosoftIgniteでAzureOpenAIの仕様が変更されてます。このコードは変更後の仕様に対応しています。
:::

```python
import streamlit as st
from openai import AzureOpenAI

client = AzureOpenAI()
USER_NAME = "user"
ASSISTANT_NAME = "assistant"
model="gpt-35-turbo"

st.title("StreamlitのChatサンプル")

def response_chatgpt(user_msg: str, chat_history: list = []):

    system_msg = """あなたはアシスタントです。"""
    messages=[
        {"role": "system", "content": system_msg}
    ]

    #チャットログがある場合は、チャットログをmessagesリストに追加
    if len(chat_history) > 0:
        for chat in chat_history:
            messages.append({"role": chat["name"], "content": chat["msg"]})
    #ユーザメッセージをmessagesリストに追加
    messages.append({"role": USER_NAME, "content": user_msg})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response

# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []


user_msg = st.chat_input("メッセージを入力")
if user_msg:
    # 以前のチャットログを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(chat["name"]):
            st.write(chat["msg"])

    # 最新のユーザメッセージを表示
    with st.chat_message(USER_NAME):
        st.write(user_msg)

    # アシスタントのメッセージを表示
    response = response_chatgpt(user_msg, chat_history=st.session_state.chat_log)
    with st.chat_message(ASSISTANT_NAME):
        assistant_msg = response.choices[0].message.content
        assistant_response_area = st.empty()
        assistant_response_area.write(assistant_msg)

    # セッションにチャットログを追加
    st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": assistant_msg})
    # チャットログを出力
    print(" ■チャットログ:")
    for chat in st.session_state.chat_log:
        print("  " + chat["name"] + ": " + chat["msg"])
```

### .envファイルに以下を記載します

```bash
AZURE_OPENAI_ENDPOINT=AzureOpenAIのエンドポイント
AZURE_OPENAI_API_KEY=AzureOpenAIのAPIキー
OPENAI_API_VERSION=2023-07-01-preview
```

## 動作確認します

VSCodeのF5でStreamlitアプリを起動させるために、.vscodeフォルダ配下のlaunch.jsonに以下を記述します。

```bash
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "debug",
            "type": "python",
            "request": "launch",
            "module": "streamlit",
            "console": "integratedTerminal",
            "args": [
                "run",
                "chat.py",
                "--server.port",
                "8501"
            ],
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

1. Pythonの仮想環境を作成します。※VSCodeであれば「ctrl+shift+p」でコマンドパレットを開き、「Python: Create Virtual Environment」を選択します。
2. VSCodeのF5でStreamlitアプリを起動します。
3. ブラウザで http://localhost:8501 にアクセスします。
4. 実際にチャットしてみましょう。このようにチャットできればOKです。

![動作確認チャット](/images/streamlit-use-openai/2023-12-24-21-42-24.png)

## まとめ

Streamlitを利用することで、簡単にOpenAIのチャットを試すことができました。
今回はローカル環境での動作確認でしたが、次回はAzureサービスにデプロイしてみます。
また、Streamlitではサイドバーなども簡単に作成できるので、サイドバーにシステムメッセージやパラメータ（例えば、temperatureなど）を設定できるようにすると、より使いやすくなると思います。