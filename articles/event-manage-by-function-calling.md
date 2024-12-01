---
title: "OpenAIのtoolsを使って、チャットベースにGoogleイベントを管理してみよう！"
emoji: "🗓️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "OpenAI", "tools", "function calling", "Google"]
published: false
---

![](/images/event-manage-by-function-calling/2024-10-16-00-27-18.png)

# はじめに

生成AIの利用用途としてのメインは、チャットアプリケーションです。
生成AIの用途はチャット以外の用途も多く事例として出ていていますが、チャットはユーザーがAIとコミュニケーションを取りやすい方法です。

そして、生成AIが知らない独自情報を回答してほしい場合は、RAGアーキテクチャが一般的です。
RAGに関する解説はこちらの記事にて。
https://zenn.dev/nomhiro/articles/sukiyanen_june_rag_func_ext_openai_gpt4o


今回は、チャットアプリでRAGするだけではなく、**チャットしながらタスクやイベントを管理出来たら面白そう！**
と思い、OpenAIのtoolsを使って、チャットベースにGoogleイベントを作成する方法を試してみました。

お試しした結果、動画のようにチャットベースでGoogleCalendarにイベントを作成することが出来ました。
https://youtu.be/LnoWLtp-UzA


# 利用するサービス

利用するサービスは、主に以下の2つです。
- フロントチャットアプリ
  - Next.js
- 生成AI
  - Azure OpenAI の Tools (Function Calling)
- Google Calendar API

## Azure OpenAI の Tools (Function Calling)

**Function Callingとは、引き渡した関数一覧と引数定義をもとに、OpenAIがユーザメッセージに対して呼び出すべき関数を選び引数を設定してくれる機能です。**

Function Callingの概要や使い方を知りたい方は、以前書いたこちらの記事を参照してください。
https://zenn.dev/nomhiro/articles/openai-tools-javascript

:::message
APIリクエスト時のパラーメータに注意が必要です。以前はfunctionsプロパティでしたが、toolsプロパティに変更になっています。
:::

:::message
OpenAI関連のアップデートは頻繁なので、調べる際は記事が書かれたタイミング、使っているバージョンにご注意ください！
:::

## Google Calendar API

APIで、GoogleCalendarのイベントを取得、登録できる機能です。

以前の記事で、GoogleCalendarAPIを使ってイベントを取得する方法を解説しています。特に、認証周りの設定はこちらを参照してください。
https://zenn.dev/nomhiro/articles/google-calendar-api

今回はイベント登録の実装をします！


# 実装していきましょう。

チャットアプリ自体の実装は長くなってしまうため、この記事では解説対象外といたします。
Nextjsを使ったチャットアプリの実装は、こちらのUdemyで学習できます。
RAGアーキテクチャを使い、Azure OpenAIのServiceを使って、チャットアプリを作成する方法を解説しています。UIの詳細な解説も含めたコースですのでぜひ参照してみてください。
https://www.udemy.com/course/ragnextjsazure-openai-servicechatgptweb/?referralCode=A4F57DBF78CE691B5523


必要な実装はこれらです。
- Google Calendar APIでイベントを登録する関数
- OpenAI の Function Callingを使って、チャット内容から呼び出す関数を選択する処理
- Function Callingで選択された関数を実行する処理

## 必要なモジュールをインストール

package.jsonに以下のモジュールを追加します。

```json
{
  "dependencies": {
    "@azure/openai": "^1.0.0-beta.12",
    "googleapis": "^143.0.0",
  }
}
```

インストールしておきましょうー

```bash
npm install
```

## Google Calendar APIでイベントを登録する関数
まず、Google Calendar APIで認証するためのcredentials.jsonを用意します。
こちらの記事で解説しています。
https://zenn.dev/nomhiro/articles/google-calendar-api#%E8%AA%8D%E8%A8%BC%E6%83%85%E5%A0%B1%E3%81%AE%E8%A8%AD%E5%AE%9A

また、今回はPoCレベルですので、NextAuthを使ってGoogleCalendarAPIの認証は行わず、上記の記事で生成されたtoken.jsonを配置しておきます。

次に、Google Calendar APIを使ってイベントを登録する関数を作成します。

```typescript
import { google } from 'googleapis';
import fs from 'fs';  
import path from 'path';  
import { OAuth2Client } from 'google-auth-library';
  
// SCPESはGoogle Calendar APIの権限を指定します。
const SCOPES = ['https://www.googleapis.com/auth/calendar'];  
// credentials.jsonとtoken.jsonのパスを指定します。
const CREDENTIALS_PATH = path.join(process.cwd(), 'credentials.json');
const TOKEN_PATH = path.join(process.cwd(), 'token.json');  

// Googleイベントの情報を格納するクラス
export class Event {
  summary: string;
  location?: string;
  description?: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };

  constructor(eventDetails: any) {
    this.summary = eventDetails.summary;
    this.location = eventDetails.location;
    this.description = eventDetails.description;
    this.start = {
      dateTime: eventDetails.start_time,
      timeZone: 'Asia/Tokyo',
    };
    this.end = {
      dateTime: eventDetails.end_time,
      timeZone: 'Asia/Tokyo',
    };
  }
}

// credentials.jsonを読み込む関数
async function loadCredentials() {  
  try {  
    const content = fs.readFileSync(CREDENTIALS_PATH, 'utf8');  
    return JSON.parse(content);  
  } catch (err) {  
    console.error('Error loading client secret file:', err);  
    throw err;  
  }  
}  

// 認証を行う関数
async function authorize(): Promise<OAuth2Client> {  
  const credentials = await loadCredentials();  
  const { client_secret, client_id, redirect_uris } = credentials.installed;  
  const oAuth2Client = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);  
  
  if (fs.existsSync(TOKEN_PATH)) {  
    const token = fs.readFileSync(TOKEN_PATH, 'utf8');  
    oAuth2Client.setCredentials(JSON.parse(token));  
  } else {  
    // 本来はユーザーに認証を求める処理を実装しますが、今回はエラーを返します。
    console.error('Authorization required. Please visit the URL and authorize the app.');
    throw new Error('Authorization required');
  }  
  
  return oAuth2Client;  
}  

// イベントを作成する関数
export const createEvent = async (event: Event): Promise<any> => {
  return new Promise(async (resolve, reject) => {
    try {
      const auth = await authorize();
      const calendar = google.calendar({ version: "v3", auth });
      
      const request = calendar.events.insert({
        calendarId: 'primary',
        requestBody: event,
      }, (err: Error | null, res: any) => {
        if (err) {
          console.error('Error creating event:', err);
          return;
        }
        console.log('Event created: %s', res.data.htmlLink);
        resolve(res.data.htmlLink);
      });
    } catch (error) {
      console.error('Error in createEvent:', error);
      reject('Failed to create event');
    }
  });
};
```

## Function Callingで関数を選択し、選択された関数を実行する

まずは、OpenAIでToolsを使って推論する関数を実装します。

```typescript
import { AzureKeyCredential, ChatCompletions, OpenAIClient } from '@azure/openai';

export const getChatCompletionsWithTools = async (messages: any[], tools: any[] ): Promise<any> => {
  console.log('start', process.env.AZURE_OPENAI_ENDPOINT!);
  return new Promise(async (resolve, reject) => {
    const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
    const azureApiKey = process.env.AZURE_OPENAI_API_KEY!;
    const deploymentId = process.env.AZURE_OPENAI_DEPLOYMENT_ID!;

    try {
      const client = new OpenAIClient(
        endpoint,
        new AzureKeyCredential(azureApiKey)
      );

      // toolsの呼び出し 
      const response = await client.getChatCompletions(
        deploymentId,
        messages,
        { 
          maxTokens: 4096,
          tools: tools,
          toolChoice: "auto",
          temperature: 0
        },
      )

      // console.log('🚀OpenAI response', response);

      resolve(response);
    } catch (error: any) {
      reject(error);
    }
  });
};
```


次に、OpenAIのFunctionCallingの関数を呼び出す処理を実装します。
toolsのJson定義と、選択された関数を実行する処理を実装します。

::: message
**OpenAIは現在の日付を知らないため、チャットで明日や明後日と指示されても日付を判断できません。**
**そのため、FunctionCallingのためのシステムメッセージで、現在日時を取得してプロンプトに入れ込みます。**
:::

```typescript
import { getChatCompletionsWithTools, getChatCompletions } from './openai';
import { Event, createEvent } from '../event-google/google';

export const Generate = async (message: string): Promise<string> => {
  return new Promise(async (resolve, reject) => {

    console.log('🚀Generate: ', message);

    var messages: any[] = [];

    // systemMessageの設定。OpenAIは現在の日付をしらないため、現在日時を取得してプロンプトに入れ込みます。
    const systemMessage = `\
    あなたはユーザのタスク管理をサポートするためのAIアシスタントです。\n\
    ユーザメッセージに対して、タスク管理のために必要なふるまいを考え、適切な関数を呼び出して回答を生成します。\n\
    現在日時：${new Date().toLocaleString()}`;
    messages.push({ role: 'system', content: systemMessage });

    // messageの設定
    messages.push({ role: 'user', content: message });

    // toolsの定義
    // 関数の名前と説明、引数の名前と説明を定義します。
    const tools = [
      {
        "type": "function",
        "function": {
          "name": "registEvent",
          "description": "GoogleCalendarにイベントを登録します。",
          "parameters": {
          "type": "object",
          "properties": {
            "summary": {
              "type": "string",
              "description": "イベントの概要",
            },
            "location": {
              "type": "string",
              "description": "イベントの場所",
            },
            "description": {
              "type": "string",
              "description": "イベントの詳細",
            },
            "start": {
              "type": "object",
              "properties": {
                "dateTime": {
                  "type": "string",
                  "description": "イベントの開始日時。形式（例）'2024-09-17T13:00:00Z' (ISO 8601形式)",
                },
                "timeZone": {
                  "type": "string",
                  "description": "イベントのタイムゾーン",
                  "default": "Asia/Tokyo",
                },
              },
              "required": ["dateTime", "timeZone"],
            },
            "end": {
              "type": "object",
              "properties": {
                "dateTime": {
                  "type": "string",
                  "description": "イベントの終了日時。形式（例）'2024-09-17T14:00:00Z' (ISO 8601形式)",
                },
                "timeZone": {
                  "type": "string",
                  "description": "イベントのタイムゾーン",
                  "default": "Asia/Tokyo",
                },
              },
              "required": ["dateTime", "timeZone"],
            },
          },
          "required": ["summary", "start", "end"],
          },
        },
      },
    ];

    // OpenAI へのリクエスト
    const result_tools = await getChatCompletionsWithTools(messages, tools);

    // toolsで呼び出す関数があれば、関数を実行
    var function_response: any;
    if (result_tools.choices[0].message?.toolCalls) {
      // ツールの実行結果をmessagesに追加
      messages.push(result_tools.choices[0].message);

      // ツールの実行結果を取得し関数を実行
      const toolCalls = result_tools.choices[0].message.toolCalls;
      toolCalls.forEach((toolCall: any) => {
        switch (toolCall.function.name) {
          // 関数名がregistEventの場合、GoogleCalendarイベントを登録
          case 'registEvent':
            // JSON文字列をパース
            const parsedObject = JSON.parse(toolCall.function.arguments);
            // Eventにマッピング
            const event: Event = {
              summary: parsedObject.summary,
              location: parsedObject.location,
              description: parsedObject.description,
              start: {
                dateTime: parsedObject.start.dateTime,
                timeZone: parsedObject.start.timeZone,
              },
              end: {
                dateTime: parsedObject.end.dateTime,
                timeZone: parsedObject.end.timeZone,
              },
            };
            // // タスク登録
            function_response = createEvent(event);
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

実装は以上です。では動かしてみましょう！！

# 実行してみよう！

.env.localにAzure OpenAIのエンドポイント、APIキー、デプロイメントIDを設定します。

```bash
AZURE_OPENAI_ENDPOINT="Azure OpenAIのエンドポイント"
AZURE_OPENAI_API_KEY="Azure OpenAIのAPIキー"
AZURE_OPENAI_DEPLOYMENT_ID="gpt-4o"

GOOGLE_CLIENT_ID="Google Calendar APIのクライアントID"
GOOGLE_CLIENT_SECRET="Google Calendar APIのクライアントシークレット"
```

実行します！
```bash
npm run dev
```

チャットアプリケーションですので、動画のようにチャットベースでGoogleCalendarにイベントを作成することが出来ました。
「明日の」と指示すると、システムメッセージで指定した日時をベースに、OpenAIが日時を推論し、FunctionCallingで引数に日付を指定してくれました。
https://youtu.be/LnoWLtp-UzA


# まとめ

OpenAIのtools(function calling)を使って、チャットベースにGoogleイベントを作成する、生成AIを仲介役としたアプリケーションを作成しました。

今回は作成のみで、FunctionCallingの関数も一つだけです。
実際には変更や削除も必要ですし、GoogleCalendarAPI以外の関数呼び出しも行う場合は、FunctionCallingの関数が増えていきます。
増えた場合には、FunctionCalling時のシステムメッセージの調整や、関数の説明文の調整、引数の説明文の調整が必要です。


OpenAIには、GPT-4o Realtime Audioなど新しい機能のモデルも出ていますので、今後さらに活用の幅が広がりそうです。
https://learn.microsoft.com/ja-jp/azure/ai-services/openai/realtime-audio-quickstart