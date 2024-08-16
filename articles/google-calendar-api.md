---
title: "GoogleCalendarのイベントをGoogleAPIを使って取得する"
emoji: "🗓️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

![](/images/google-calendar-api/2024-08-16-10-07-06.png)

# はじめに
■モチベーション
- 自前のWebアプリケーションから、GoogleCalendarに登録しているイベント情報を取得したい。

**→この記事では、PythonコードでGoogleCalendarAPIを使って、検証目的でGoogleCalendarに登録しているイベント情報を取得する方法を解説します。**

# 前提
- 実行環境：VSCode
- Python：3.11

# GoogleAPIの設定
まず、GoogleAPIを使うためにGoogleCloudコンソールでプロジェクトを作成し、GoogleCalendarAPIを有効化し認証周りを設定します。

## プロジェクト作成
GoogleCloudコンソールにアクセスし、新しいプロジェクトを作成します。
https://console.cloud.google.com/
![alt text](/images/google-calendar-api/image-11.png)

## Google Calendar API有効化
Google Calendar APIを検索し、
![alt text](/images/google-calendar-api/image-12.png)

Google Calendar APIをを有効にします。
![alt text](/images/google-calendar-api/image-13.png)

## OAuth認証同意画面の構成
Google Calendar APIにアクセスする際のOAuth認証同意画面の設定をします。
UserTypeは「外部」にし、後からテストユーザを指定します。
![alt text](/images/google-calendar-api/image.png)

登録するアプリ名とユーザサポートメールアドレスを入力します。
![alt text](/images/google-calendar-api/image-3.png)

![alt text](/images/google-calendar-api/image-2.png)

スコープは設定しません。
テストユーザはこの時点では設定していませんが、後ほど設定します。
![alt text](/images/google-calendar-api/image-4.png)

OAuth同意画面の設定完了です。
![alt text](/images/google-calendar-api/image-5.png)

## 認証情報の設定
認証のためのOAuthクライアントIDを作成します。
![alt text](/images/google-calendar-api/image-6.png)

![alt text](/images/google-calendar-api/image-7.png)


ダウンロードした JSON ファイルを credentials.json として保存します。
![](/images/google-calendar-api/2024-08-16-09-05-18.png)


## テストユーザ作成
APIを使用できるテストユーザを指定します。
![alt text](/images/google-calendar-api/image-15.png)

![alt text](/images/google-calendar-api/image-16.png)

# GoogleCalendarのイベントを取得するPythonコード

こちらがGoogleCalendarのイベントを取得するPythonコードです。

```Python
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# APIに要求する権限を指定
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def main():
  """
  ユーザーのカレンダーの現在時刻から10件のイベントの開始日時と名前を表示する。
  """
  creds = None
  # ユーザーのアクセスとリフレッシュトークンを格納するtoken.jsonファイルが存在する場合、token.jsonを使用して認証する。
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # 有効な資格情報がない場合、ユーザーにログインさせます。
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # 次回実行のために資格情報を保存する。※二回目以降の実行では認証がスキップされる。
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # カレンダーAPIを呼び出します。
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z'はUTC時間を示します
    print("次の10件のイベントを取得中")
    events_result = (
      service.events()
      .list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
      )
      .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("次のイベントはありません。")
      return

    # 次の10件のイベントの開始日時と名前を表示します。
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"エラーが発生しました: {error}")


if __name__ == "__main__":
  main()
```

Pythonコードを実行しましょう。
実行すると以下のように、Googleにログインする認証画面が表示されます。

![alt text](/images/google-calendar-api/image-9.png)

![alt text](/images/google-calendar-api/image-10.png)

![alt text](/images/google-calendar-api/image-14.png)

テストモードなので以下のようなメッセージが出ます。続行を押します。
![alt text](/images/google-calendar-api/image-17.png)

続行して、アクセス権を付与します。
![alt text](/images/google-calendar-api/image-18.png)

Completeとなり、VSCodeで実行したPythonコードにリダイレクトされる。
![alt text](/images/google-calendar-api/image-19.png)

GoogleCalendarに登録しているイベント10件が取得できました。
![alt text](/images/google-calendar-api/image-20.png)


# 参考
- https://developers.google.com/calendar/api/quickstart/python?hl=ja