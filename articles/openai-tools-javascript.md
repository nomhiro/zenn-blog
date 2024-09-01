---
title: "JavaScriptでAzureOpenAIのFunctionCalling(Tools)を使う際の注意点"
emoji: "💣"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "OpenAI", "JavaScript", "FunctionCalling", "Tools"]
published: false
---

# 背景
:::message
OpenAI関連はアップデートが早いため、実装の際は公式ドキュメントを参照してください。
:::

OpenAIには、Function Calling 機能があります。
後述のようにtoolsプロパティを使って呼び出すのですが、JavaScriptで実装していた際にはまったことがあるので、注意点をまとめておきます。
:::message alert
結論を先にいうと、**OpenAIにリクエストする際のmessageパラメータにて、roleが"tool"の場合は "toolCallId" を指定する必要があります。**
※エラーメッセージでは "tool_call_id" が必須だ。となり気が付きにくいです。
※pythonでは "tool_call_id" です。
:::

# そもそもFunction Callingとは

Function Callingの概要や使い方を知りたい方は、これらの記事を参照してください。
:::message
APIリクエスト時のパラーメータに注意が必要です。以前はfunctionsプロパティでしたが、toolsプロパティに変更になっています。
:::

:::message
OpenAI関連のアップデートは頻繁なので、調べる際は記事が書かれたタイミング、使っているバージョンにご注意ください！
:::

Azureのページはこちらです。Pythonを使ったサンプルが掲載されています。
https://learn.microsoft.com/ja-jp/azure/ai-services/openai/how-to/function-calling?tabs=python
Function Callingの概要を知りたい方はこちら！
https://zenn.dev/microsoft/articles/azure-openai-add-function-calling
toolsプロパティに変更になった内容についてはこちらで述べられてます。
https://zenn.dev/microsoft/articles/azure-openai-tools


# Function Callingの扱い方

Function Callingを使う場合は、「Function Calling API呼び出し」と「関数実行」（オレンジと青の線）までは必ず実行します。
ユースケースによっては、関数を実行して終了する場合もありますが、ユーザメッセージに対する応答を推論する場合は、関数実行後に「推論」のためにAPIを呼び出します。（緑色の線）
![](/images/openai-tools-javascript/2024-09-01-20-58-51.png)

最後の推論では、OpenAI呼び出し時のパラメータ messages に以下を含める必要があります。
- ユーザメッセージ
- 関数実行の結果
- 関数実行の結果のメタデータ

## 注意点
最後の推論で「関数実行の結果のメタデータ」を指定する際に、SDKごとにパラメータ名が異なっています。
Microsoftのドキュメントで示されているPythonのSDKでは以下のように指定します。
- role: "tool"を指定します。
- tool_call_id: 選ばれた関数のidを指定します。
- name: 関数の名前を指定します。
- content: 関数の実行結果を指定します。
```python
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": time_response,
})
```

これを参考にJavaScriptで実装しました。
```javascript
messages.push({
  role: "tool",
  tool_call_id: toolCall.id,
  content: toolCall.function.arguments,
});
```

この実装をして実行すると、以下のエラーになります。
roleに "tool" を指定する場合は、"tool_call_id" が必須だ。と怒られます。
いや、上述の通り、指定しとるわ！！！と、1時間くらい格闘してました。
```powershell
⨯ unhandledRejection: {
  message: "Missing parameter 'tool_call_id': messages with role 'tool' must have a 'tool_call_id'.",
  type: 'invalid_request_error',
  param: 'messages.[3].tool_call_id',
  code: null
}
```

よくよくSDKの中身を追うと、スキーマの定義が以下のようになっています。
はい、toolCallIdですね。JavaScriptに慣れていないのと、エラーメッセージが違うので、気が付きづらかったです...
```javascript
/** A request chat message representing requested output from a configured tool. */
export declare interface ChatRequestToolMessage extends ChatRequestMessage {
    /** The chat role associated with this message, which is always 'tool' for tool messages. */
    role: "tool";
    /** The content of the message. */
    content: string | null;
    /** The ID of the tool call resolved by the provided content. */
    toolCallId: string;
}
```

なので、以下のように修正して実行すると、エラーが解消されました。
```javascript
messages.push({
  role: "tool",
  toolCallId: toolCall.id,
  content: toolCall.function.arguments,
});
```

# 参考
- 以下は、Function Callingを呼び出し関数実行し、最後に推論を行う実装例です。
:::details 実装例
```javascript
import { AzureKeyCredential, OpenAIClient } from '@azure/openai';
import { getChatCompletionsWithTools, getChatCompletions } from './openai';
import { createEvent } from './google'
import { json } from 'stream/consumers';

export const Generate = async (message: string): Promise<string> => {
  return new Promise(async (resolve, reject) => {
    const endpoint = process.env.AZURE_OPENAI_API_ENDPOINT!;
    const azureApiKey = process.env.AZURE_OPENAI_API_KEY!;
    const deploymentId = process.env.AZURE_OPENAI_API_DEPLOYMENT_NAME!;

    console.log('🚀Generate: ', message);

    var messages: any[] = [];

    // systemMessageの設定
    const systemMessage = `\
    あなたはユーザのタスク管理をサポートするためのAIアシスタントです。\n\
    ユーザメッセージに対して、タスク管理のために必要なふるまいを考え、適切な関数を呼び出して回答を生成します。\n\
    現在日時：${new Date().toLocaleString()}`;
    messages.push({ role: 'system', content: systemMessage });

    // messageの設定
    messages.push({ role: 'user', content: message });

    // toolsの定義
    const tools = [
      {
        "type": "function",
        "function": {
          "name": "createEvent",
          "description": "Googleカレンダーにイベントを作成します。タ",
          "parameters": {
            "type": "object",
            "properties": {
              "summary": {
                "type": "string",
                "description": "タスク名",
              },
              "description": {
                "type": "string",
                "description": "タスクの詳細",
              },
              "start": {
                "type": "object",
                "properties": {
                  "dateTime": {
                    "type": "string",
                    "description": "タスクの開始日時",
                  },
                  "timeZone": {
                    "type": "string",
                    "description": "必ずAsia/Tokyoを指定する",
                  },
                },
              },
              "end": {
                "type": "object",
                "properties": {
                  "dateTime": {
                    "type": "string",
                    "description": "タスクの終了日時",
                  },
                  "timeZone": {
                    "type": "string",
                    "description": "必ずAsia/Tokyoを指定する",
                  },
                },
              },
            },
            "required": ["summary", "start", "end"],
          }
        }
      },
    ];

    // OpenAI へのリクエスト
    const result_tools = await getChatCompletionsWithTools(messages, tools);

    console.log('🚀result_tools: ', JSON.stringify(result_tools));

    // toolsで呼び出す関数があれば、関数を実行
    var function_response: any;
    if (result_tools.choices[0].message?.toolCalls) {
      // ツールの実行結果をmessagesに追加
      messages.push(result_tools.choices[0].message);

      // ツールの実行結果を取得し関数を実行
      const toolCalls = result_tools.choices[0].message.toolCalls;
      toolCalls.forEach((toolCall: any) => {
        switch (toolCall.function.name) {
          case 'createEvent':
            // Googleカレンダーにイベントを作成
            console.log('🚀createEvent: ', toolCall.function.arguments);
            // イベント作成関数の実行
            createEvent(toolCall.function.arguments);
            function_response = `以下イベントを登録しました。\n${toolCall.function.arguments}`;
            console.log('🚀function_response: ', function_response);
            break
          default:
            function_response = "関数が見つかりませんでした。";
            break
        } 
        messages.push({
          role: "tool",
          toolCallId: toolCall.id,
          content: toolCall.function.arguments,
        });

      });
    }

    console.log('🚀messages: ', messages);

    // toolsの呼び出し結果をもとに回答を生成
    const result = await getChatCompletions(messages);

    resolve(result.choices[0].message.content);
  });
};
```
:::