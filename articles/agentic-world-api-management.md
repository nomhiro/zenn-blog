---
title: "DurableFunctionsとAPIManagementを使ったAgentAPI管理による Agentic World を考える"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "APIManagement", "DurableFunctions", "Agent", "LLM"]
published: false
---

# はじめに

生成AIの実用のために、**AI Agent** という言葉をよく聞くようになりましたね。人間の代わりに行動できる AI Agent を組み合わせた世界を、Microsoftは Agentic World と呼んでいました。
こちらが与えた指示を解釈して実行するソフトウェアが AI Agent です。とはいえ、今までできなかったことが劇的にできるようになったわけではありません。
私の解釈ですが、1つのAgentで多くのことを実行させようとすると、指示を解釈する精度や推論する精度、タスク実行の精度が下がります。そのため、**分野やタスクごとに専門家Agentを作り、それを組み合わせてタスクを実行するというのが現時点の現実解**でしょう。

# 専門家Agentとオーケストレーション

複数の専門家Agentを組み合わせてタスクを実行するためには、**ユーザからの指示に対してどの専門家Agentを使い、どのようなInputで専門家Agentを呼び出すか**を決定する必要があります。その役割も1つの専門家Agentが担います。マルチエージェントフレームワークでは、マネージャーエージェントと呼ばれることがあります。

マルチエージェントのフレームワークはいくつか出てきています。
- AutoGen
- Magentic-One
- LangGraph
- LlamaIndex
- CrewAI

それぞれのフレームワークの違いは比較は、他の皆さんが書かれたブログを参考にしてみてください。
https://qiita.com/Dataiku/items/4dbdec1f5046cc415ffc
https://zenn.dev/chips0711/articles/47ae142e51511b

複数のエージェントを使ったソリューションが、上記のフレームワークで実現できるのであれば、フレームワークを使い実装少なくできるため、それが手っ取り早いと思います。
しかし業務上のシナリオでは、フレームワークだけだと痒いところに手が届かず、、というシーンもあります。
その場合は、一から実装することになります。この記事では以下のようなマルチエージェントの思想で考えます。大前提は、**ワークフローは事前に定義する**ことです。
理由はこれらです。これらを考慮すると、業務を分析しその流れに沿ったワークフローを組むことが最も確実です。
- マネージャエージェントのような、エージェントを完全に自動でLLMに考えさせて動的に実行させると、業務上の仕事を代替させる際には、**ブレが発生してしまい信頼性が低くなる**可能性があります。
- ある業務をエージェントに代替させる場合には、**どのようなフローで業務が成り立っているのかを分割して分析**する必要があります。そうでなければ、マルチエージェントの過程や結果を判断できません。

ここで、ワークフローを事前に定義する仕組みとして利用できるのが、Azure Durable Functionsです。
Durable Functionsは、**複数のタスクを組み合わせたワークフローを実装**できます。また、**タスクエラー時の再実行性**もDurable Functions自体に組み込まれています。
https://learn.microsoft.com/ja-jp/azure/azure-functions/durable/durable-functions-overview?tabs=in-process%2Cnodejs-v3%2Cv1-model&pivots=csharp#application-patterns

Durable Functionsだけを推しているように見えますが、Durable Functionsのタスクはコードによる実装なので、様々なライブラリを利用できます。つまり、**LangChainやAutoGenなどをワークフローの一部に組み込んでもよい**わけです。

今までのことを概念図にするとこのようなイメージです。
![](/images/agentic-world-api-management/2025-01-12-00-22-00.png)


オーケストレーション層には以下の機能が必要になります。
- マネージャーエージェントによる専門家Agentの選択
- (option)マネージャーエージェントによる専門家AgentのAPIのInputパラメータ生成
- 選ばれた専門家Agentの呼び出し
- 専門家Agentの結果を統合
- 専門家Agentのエラーハンドリングと再実行制御

#### （参考）トヨタ自動車のO-Beyaシステム
Microsoft Ignite 2024にて、トヨタ自動車がマルチエージェントシステムの**O-Beya**を発表しており、**Durable Functions**がワークフロー定義（オーケストレーション層）として使われています。
https://www.bing.com/search?pglt=299&q=Toyota+O-Beya+Microsoft&cvid=1274a4f596244ac3816c6e5afde3fa79&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBCDQ3NTBqMGoxqAIIsAIB&FORM=ANNTA1&PC=U531

https://devblogs.microsoft.com/cosmosdb/toyota-motor-corporation-innovates-design-development-with-multi-agent-ai-system-and-cosmos-db/

# どういう組織体制で開発する？
規模の大きい組織が各エージェントの開発を行い、エージェントを組み合わせたマルチエージェントシステムを構築する場合、どうしたらよいでしょう？
個々のエージェントを担当する開発チームが、それぞれでマルチエージェントの仕組みを持つのは非効率です。※もちろん、ある業務に特化したシナリオに対応する場合はそのチームが開発するのが一番です。
最も良いのは、**各開発チームが開発したエージェントが、共通的なマルチエージェントの仕組みに組み込みできること**です。
その場合、組織としては二つに分かれるでしょう。
- **オーケストレーション層を開発する組織**
- **各専門家Agentを開発する複数の組織**

そうなってくると、それぞれの組織は互いが疎結合に開発できないと困ります。


# マイクロサービスな専門家Agent
**オーケストレーション層を開発する組織** と **各専門家Agentを開発する複数の組織** が疎結合に開発するためには、仕組みとしてオーケストレーション層と各専門家Agent群が疎結合になっている必要があります。

マイクロサービスとは、小さく分離された、疎結合なサービスを指します。マイクロサービスな専門家Agentを作成することで、オーケストレーション層の開発と各専門家Agentの開発を別々の開発チームが独立して開発できますし、リリースにおいても他の専門家Agentに影響を最小限にして、専門家Agentを更新できます。

必要な要件はこれらとします。
- **専門家Agentは小さく、独立的で、疎結合**である。
- **小規模な開発者チームで専門家Agentを作成および管理**できる。
- **専門家Agentで個別にテスト、精度確認**できる
- **専門家Agentは個別にデプロイ**できる。
- **専門家AgentはRestAPIを使い互いに通信**する。各専門家Agent内部の実装の詳細は、オーケストレーション及び他の専門家Agentには隠蔽される。
- **専門家Agentは、同じ技術スタック、ライブラリ、またはフレームワークを共有する必要はない**。

また、専門家Agentは、一気に作成できるものではなく、実用しながら少しずつ増えていくものです。専門家Agentが追加された場合に、オーケストレーション側の実装に毎回専門家Agentの呼び出し実装をするのは非効率です。
そのため、**専門家AgentのAPIを可能な限り共通化して管理し、専門家Agentの追加に伴うオーケストレーション側の変更を最小限に**する必要があります。
共通化という観点では、オーケストレーション側と専門家Agent間はRestAPIで呼び出されるため、**APIの共通的な最小限のルール決めが必要**そうです。一方で、専門家Agentを開発する組織は、ある特定の業務に特化した専門家Agentを作成するため、必ずしもその共通的なAPIルールに乗っ取れない場合があります。
管理という観点では、専門家Agentの一元管理や呼び出し回数制限、ログ集約などが必要です。

# Azure API Managementを使った専門家AgentのAPI管理
AzureのAPI Managementは、APIの公開、APIの管理、APIのモニタリング、APIのセキュリティ、APIの分析などを行うためのサービスです。API Managementを使うことで、APIの共通化や管理を行うことができます。
また、headerやBodyなどの変換ルールも記述できるため、専門家AgentのAPIの共通化を行うことができます。
https://learn.microsoft.com/ja-jp/azure/api-management/api-management-key-concepts

以下がAPI Managementを組み入れたアーキテクチャ図です。
![](/images/agentic-world-api-management/2025-01-09-23-11-03.png)

ポイントはこれらです。
- **それぞれの開発チームが独立して開発できること**
- **専門家Agentが追加されたとしても、他の専門家やオーケストレーション側に実装せずに済むようにする**

そして、API Managementに任せる役割はこれらです。今回は太字の1,2に焦点を当てて進めます。
1. **専門家AgentのAPIの公開**
2. **専門家AgentのAPIのRequestパラメータの変換**
3. API呼び出し制限による専門家Agentの負荷及び課金制限
4. 各専門家Agentの呼び出しログの取得

::: message
API Managementの変換ポリシーは、XMLの中にC#コードを記述するという、管理面がいまいちな仕様になっています。
そのため、複雑な変換が必要な場合は、API Managementではなく別の手段（APIルールに則ったAPIを作成する、変換ロジックを専門家Agent側で用意する）などしたほうがよいです。
:::

# 実践あるのみ！

Agentによる課題解決のユースケースは以下を想定します。一般的なはなしにするために、なんらかの課題に対して意見をもらいタスクに起こし印刷用タスクリストにするフローを想定します。
具体的なシーンとしては、ご家庭の年末大掃除をイメージしました。（書いてるのが2024年の年末なので....）

このようなワークフローを想定します。
![](/images/agentic-world-api-management/2025-01-12-00-40-29.png)

以下の専門家Agentを用意します。（専門家Agentの作り方に関する記事ではないので、決まった回答をするスタブで用意します。）
- **空調機器について詳しい**専門家Agent
- **キッチンの機器について詳しい**専門家Agent
- **お風呂の機器について詳しい**専門家Agent
- **タスクを管理する**専門家Agent
- **印刷用タスクリストを作成する**機能

これらのAgentをAPI Managementを使って公開し、Durable Functionsを使ったオーケストレーションから実行します。

以下の順序で進めていきます。
1. 専門家AgentのAPIの作成 ※今回はスタブとして仮APIを用意します
2. Azure Functions に専門家Agentをデプロイ
3. API Managementの作成
4. API Management に専門家Agent をインポート。
5. 共通的なAPIで呼び出せるように変換ポリシーを設定
6. Azure Functions の Durable Functions を使ったAgentオーケストレーションの作成
7. 動作確認

## 事前の決めごと
API Management でAPIを共通化する前に、最低限のAPIのルールを決めておく必要があります。つまり、Durable Functionsによるオーケストレーションの実装をせずとも専門家AIを追加するために、**オーケストレーション側が想定するAPIの仕様**を決めます。オーケストレーション側は、以下のルールにしたがって実装します。**専門家APIが追加されたとしても、オーケストレーション側の実装は修正しない**で済みます。

#### APIルール
```
- POSTメソッド
- Request Body
  - messages: list　※過去のチャット履歴と、最新のユーザメッセージ（指示文）を含むリスト
    - role: string
    - content: string
- Response Body
  - status: string
  - inference: string　※専門家Agentの推論結果
```

## 1. 専門家AgentのAPIの作成
それでは、まずは専門家AgentのAPIを作成します。今回は決まった応答を返すスタブAPIです。

#### 空調機器の専門家Agent
このAgentはAPIルール通りに作られたAgentです。
```
Request Body:
  - messages: list  ※過去のチャット履歴と、最新のユーザメッセージ（指示文）を含むリスト
    - role: string
    - content: string
Response Body:
  - status: string
  - inference: string  ※専門家Agentの推論結果
```

#### キッチン機器の専門家Agent
RequestやReponseのパラメータ名がAPIルールと異なるAgentです。**API Managementの変換ポリシーで変換**します。
```
Request Body:
  - message_list: list  ※★ルールと異なるパラメータ名
    - role: string
    - content: string
Response Body:
  - status: string
  - output_content: string  ※★ルールと異なるパラメータ名
```

#### お風呂機器の専門家Agent
RequestやReponseのパラメータ名がAPIルールと異なるAgentです。**API Managementの変換ポリシーで変換**します。
```
Request Body:
  - messages: list
    - type: string
    - message: string
Response Body:
  - status: string
  - result: object  ※★ルールと異なるパラメータ名
    - message: string  ※★ルールと異なるパラメータ名
    - reference_url: string  ※★ルールと異なるパラメータ名
```

一応載せておきますが、スタブなので見る必要ないレベルです。決まった回答を返します。
::: details 専門家AgentのPythonコード
```python
import azure.functions as func
import logging
import json
import time
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

logging.basicConfig(level=logging.INFO)

DL_URL_BASE = os.environ.get("DL_URL_BASE")


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    @classmethod
    def from_dict(cls, data: dict):
        if 'role' not in data:
            raise TypeError("Missing 'role' in message data")
        if 'content' not in data:
            raise TypeError("Missing 'content' in message data")
        return cls(role=data.get('role'), content=data.get('content'))

    def __str__(self):
        return f"Message(role={self.role}, content={self.content})"


@app.route(route="agent_airconditioner", methods=["POST"])
def agent_airconditioner(req: func.HttpRequest) -> func.HttpResponse:
    """
    POSTメソッド
    Request Body:
      - messages: list  ※過去のチャット履歴と、最新のユーザメッセージ（指示文）を含むリスト
        - role: string
        - content: string
    Response Body:
      - status: string
      - inference: string  ※専門家Agentの推論結果
    """
    try:
        req_body = req.get_json()
        if isinstance(req_body, str):
            req_body = json.loads(req_body)
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON in request body.",
            status_code=400
        )

    logging.info(f"req_body: {req_body}")

    messages_data = req_body.get('messages')
    if not messages_data:
        return func.HttpResponse(
            "Missing 'messages' in request body.",
            status_code=400
        )

    # Messageリスト内オブジェクトが正しいか確認
    try:
        messages = [Message.from_dict(
            message) for message in messages_data]
    except TypeError as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )

    # ログ出力
    for message in messages:
        logging.info(f" meessage: {message}")

    # 15秒待機
    time.sleep(15)

    # Placeholder for inference logic
    inference_result = """空調のメンテナンス方法は以下の通りです。

### 吹出・吸込グリルのフィルター掃除
- 掃除表示が点灯したら清掃を開始: リモコンの掃除表示が点灯した時に、吸込グリルのフィルターを掃除します。
- フィルターの水洗い: 吸込グリルのフィルターを取り外して水洗いします。
- グリルカバー及び本体の清掃: グリルカバーや本体は、定期的に拭き掃除をします。

### 清掃手順
- 床付吸込グリル: フィルターを取り外し、水洗いします。
- 壁付吸込グリル: 前面カバーを外してフィルターを取り出し水洗いします。
- 天井付吸込グリル: グリルカバーを左に回して外し、フィルターを取り出し水洗いします。

### 注意事項
- 濡れたフィルターは陰干しで乾燥させてから再度取り付けます。
- 機械油のブラシや掃除機のノズルでフィルターに押しつけないでください。
- グリルや本体の汚れがある場合は、水拭きを推奨します。
- 定期的なメンテナンスで空調を安全に使用しましょう。"""

    response_body = {
        "status": "success",
        "inference": inference_result
    }

    logging.info(f"response_body: {response_body}")

    return func.HttpResponse(
        json.dumps(response_body, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="agent_kichen", methods=["POST"])
def agent_kichen(req: func.HttpRequest) -> func.HttpResponse:
    """
    POSTメソッド
    Request Body:
      - message_list: list  ※★ルールと異なるパラメータ名
        - role: string
        - content: string
    Response Body:
      - status: string
      - output_content: string  ※★ルールと異なるパラメータ名
    """
    try:
        req_body = req.get_json()
        if isinstance(req_body, str):
            req_body = json.loads(req_body)
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON in request body.",
            status_code=400
        )

    logging.info(f"req_body: {req_body}")

    messages_data = req_body.get('message_list')
    if not messages_data:
        return func.HttpResponse(
            "Missing 'message_list' in request body.",
            status_code=400
        )

    # Messageリスト内オブジェクトが正しいか確認
    try:
        messages = [Message.from_dict(
            message) for message in messages_data]
    except TypeError as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )

    # ログ出力
    for message in messages:
        logging.info(f" meessage: {message}")

    # 20秒待機
    time.sleep(20)

    # Placeholder for inference logic
    output_message = """IHクッキングヒーターのメンテナンス方法は以下の通りです。
- トッププレートの汚れは、柔らかい布で水拭きしてください。
- 頑固な汚れには、クリームクレンザーを少量使ってアルミホイルを丸めたものでこすり落とし、その後水拭きします。
- 操作パネルは乾いた布で拭いて、汚れを取り除きます。
- 注意事項として、火傷を避けるためにお手入れは電源スイッチを切り、本体が冷えてから行うことが重要です。また、お手入れにベンジンやシンナーなどは使わないでください。"""

    response_body = {
        "status": "success",
        "output_content": output_message
    }

    logging.info(f"response_body: {response_body}")

    return func.HttpResponse(
        json.dumps(response_body, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )


class MessageBathroom:
    def __init__(self, type: str, message: str):
        self.type = type
        self.message = message

    @classmethod
    def from_dict(cls, data: dict):
        if 'type' not in data:
            raise TypeError("Missing 'type' in message data")
        if 'message' not in data:
            raise TypeError("Missing 'message' in message data")
        return cls(type=data.get('type'), message=data.get('message'))

    def __str__(self):
        return f"MessageBathroom(role={self.type}, content={self.message})"


@app.route(route="agent_bathroom", methods=["POST"])
def agent_bathroom(req: func.HttpRequest) -> func.HttpResponse:
    """
    POSTメソッド
    Request Body:
      - messages: list
        - type: string
        - message: string
    Response Body:
      - status: string
      - result: object  ※★ルールと異なるパラメータ名
        - message: string  ※★ルールと異なるパラメータ名
        - reference_url: string  ※★ルールと異なるパラメータ名
    """
    try:
        req_body = req.get_json()
        if isinstance(req_body, str):
            req_body = json.loads(req_body)
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON in request body.",
            status_code=400
        )

    logging.info(f"req_body: {req_body}")

    messages_data = req_body.get('messages')
    if not messages_data:
        return func.HttpResponse(
            "Missing 'messages' in request body.",
            status_code=400
        )

    # Messageリスト内オブジェクトが正しいか確認
    try:
        messages = [MessageBathroom.from_dict(
            message) for message in messages_data]
    except TypeError as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )

    # ログ出力
    for message in messages:
        logging.info(f" meessage: {message}")

    # 25秒待機
    time.sleep(25)

    # Placeholder for inference logic
    result_message = """お風呂のメンテナンス方法は以下の通りです。
### 毎日のお手入れの基本
- 少し熱めのシャワーをかけて汚れを洗い流します。
- 床から1mの高さまでは特に汚れがつきやすいので念入りに洗います。
- ドアには直接水をかけないよう注意してください。
- こびりついた汚れはスポンジでやさしくこすり落とします。
- 水のシャワーをかけて浴室内の温度を常温程度に下げます。
- 残った水分をふき取り、窓を開けるか換気扇を回します。
- 十分に換気してください。

### 浴室の床のお手入れの仕方 石鹸カス、カルシウム、ミネラルの汚れ
- クエン酸を使用します。
- 床を濡らし、クエン酸をふりかけて30分置きます。
- 重曹をふりかけて、先割れ加工の浴室用ブラシでこすります。
- 重曹をふりかけると発砲しますが、これは中性になるときの反応です。"""

    response_body = {
        "status": "success",
        "result": {
            "message": result_message,
            "reference_url": "https://reference_url_sample"
        }
    }

    logging.info(f"response_body: {response_body}")

    return func.HttpResponse(
        json.dumps(response_body, ensure_ascii=False),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="agent_taskmanagement", methods=["POST"])
def agent_taskmanagement(req: func.HttpRequest) -> func.HttpResponse:
    """
    POSTメソッド
    Request Body:
      - messages: list  ※過去のチャット履歴と、最新のユーザメッセージ（指示文）を含むリスト
        - role: string
        - content: string
    Response Body:
      - status: string  ※Actionの実行結果
      - inference: string  ※Actionの実行結果の詳細
    """
    try:
        req_body = req.get_json()
        if isinstance(req_body, str):
            req_body = json.loads(req_body)
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON in request body.",
            status_code=400
        )

    logging.info(f"req_body: {req_body}")

    messages_data = req_body.get('messages')
    if not messages_data:
        return func.HttpResponse(
            "Missing 'messages' in request body.",
            status_code=400
        )

    # Messageリスト内オブジェクトが正しいか確認
    try:
        messages = [Message.from_dict(
            message) for message in messages_data]
    except TypeError as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )

    # ログ出力
    for message in messages:
        logging.info(f" meessage: {message}")

    # 10秒待機
    time.sleep(10)

    # Placeholder for action execution logic
    action_result = "success"
    inference = """### 空調メンテナンス
1. 吸込グリルのフィルター掃除
   - フィルターを取り外し水洗い
   - フィルターを陰干し
2. 吹出・吸込グリルカバーおよび本体の掃除
   - 定期的な拭き掃除
3. 掃除表示の確認とリセット
   - リモコンの掃除表示が点灯しているか確認

### IHクッキングヒーターのメンテナンス
1. トッププレートの掃除
   - 柔らかい布で水拭き
   - 頑固な汚れにはクリームクレンザーとアルミホイルを使用
2. 操作パネルの掃除
   - 乾いた布で拭く
3. 注意事項の確認
   - 火傷を避けるため、電源を切り、本体が冷えてから掃除

### 浴室のメンテナンス
1. 毎日のお手入れ
   - 熱めのシャワーで汚れを洗い流す
   - スポンジでこびりついた汚れを優しくこすり落とす
   - 浴室内を常温に冷やし、水分を拭き取り、換気
2. 浴室の床掃除
   - 石鹸カス、カルシウム、ミネラルの汚れにクエン酸を使用
   - 重曹をふりかけてブラシでこすり、発泡させて中和"""
    output_url = DL_URL_BASE + "?task_id=task_sample"

    logging.info(f"action_result: {action_result}")

    return func.HttpResponse(
        json.dumps({
            "status": action_result,
            "inference": inference,
            "output_url": output_url
        }, ensure_ascii=False),
        status_code=200,
        mimetype="application/json"
    )


@app.route(route="download_task", methods=["GET"])
def download_task(req: func.HttpRequest) -> func.HttpResponse:
    """
    GETメソッド
    Request Parameters:
        - task_id: string
    Response Body:
        - file_contents: binary  ※タスク成果物のファイル
    """

    task_id = req.params.get('task_id')
    if not task_id:
        return func.HttpResponse(
            "Missing 'task_id' in request parameters.",
            status_code=400
        )

    file_path = f"./{task_id}.csv"
    if not os.path.exists(file_path):
        return func.HttpResponse(
            "File not found.",
            status_code=404
        )

    with open(file_path, 'rb') as file:
        file_content = file.read()

    return func.HttpResponse(
        file_content,
        status_code=200,
        mimetype="application/octet-stream",
        headers={
            'Content-Disposition': f'attachment; filename={task_id}.csv'
        }
    )
```

:::

## 2. Azure Functions に専門家Agentをデプロイ
今回は、1つのAzure Functionsにすべての専門家Agentをデプロイします。
各開発チームが、異なるスケジュールで並行して専門家Agentを作成することが多いです。その場合は、専門家AgentごとにAzure Functionsを用意するのが良いでしょう。

デプロイしてあります。※Flex Consumptionプラン、日本リージョンに来てほしいですね
![](/images/agentic-world-api-management/2025-01-12-00-51-01.png)

## 3. API Managementの作成
この記事ではAPI Managementが重要なぽいんとなので、キャプチャを載せておきます。

まずリソース名や価格レベルを指定します。
検証用途なので、価格レベルは「Developer」を指定します。**API Managementは全体的に高めですので、用途に応じて適切に使い分けましょう**。専門家Agentの量や費用対効果によって導入有無が変わるかもしれません。
https://azure.microsoft.com/ja-jp/pricing/details/api-management/?msockid=2ded0802190e6e23183c1d4318536fb4
https://learn.microsoft.com/ja-jp/azure/api-management/api-management-features
![](/images/agentic-world-api-management/2025-01-10-19-34-05.png)

ログの設定をしておきます。
![](/images/agentic-world-api-management/2025-01-10-19-34-58.png)

検証用途なので「なし」
![](/images/agentic-world-api-management/2025-01-10-20-14-44.png)

これでデプロイします。
![](/images/agentic-world-api-management/2025-01-10-20-15-20.png)

### 4. API Management に専門家Agent をインポート
次にAPIを追加します。Function Appを選択することで、ボタンぽちぽちだけでインポートできます。楽ちんですね。
他にも、OpenAI Service自体のAPIをインポートすることもできます。Functionsなどにデプロイしていないサービスについては、OpenAPI仕様などでインポートできます。
![](/images/agentic-world-api-management/2025-01-10-21-22-57.png)

「Browse」から対象のFunctionを選択します。
![](/images/agentic-world-api-management/2025-01-10-21-24-01.png)

対象のFunctionsを選択し、APIを選択します。
![](/images/agentic-world-api-management/2025-01-10-21-25-58.png)

![](/images/agentic-world-api-management/2025-01-10-21-26-49.png)

API実行のために、API Managementのサブスクリプションキーを取得しておきます。
![](/images/agentic-world-api-management/2025-01-11-10-31-15.png)

## 5. 共通的なAPIで呼び出せるように変換ポリシーを設定
空調機器の専門家AgentはAPIルール通りに作られたAgentなので変換不要です。

キッチン機器の専門家Agentとお風呂機器の専門家Agentは、APIルールと異なるため、API Managementの変換ポリシーで変換します。
Inbound processingのポリシーを設定します。
![](/images/agentic-world-api-management/2025-01-12-09-16-10.png)

ポリシーはXMLで記述します。APIルールの通りにAPIManagementにRequestされたBoduを、キッチン機器の専門家AgentのBodyに変換します。
- Request Body の messages リストフィールドを、message_list に変換
- Response Body の output_content フィールドを、inference に変換
```xml
<policies>
    <inbound>
        <base />
        <set-backend-service id="apim-generated-policy" backend-id="agenticworld-agents-api" />
        <set-body>@{
                var bodyString = context.Request.Body.As<string>(preserveContent: true);
                JObject requestBody = null;

                requestBody = Newtonsoft.Json.JsonConvert.DeserializeObject<JObject>(bodyString);

                // Transforming request body if the field exists
                if (requestBody != null && requestBody["messages"] != null)
                {
                    requestBody["message_list"] = requestBody["messages"];
                    requestBody.Remove("messages");
                }

                return requestBody.ToString();
            }</set-body>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
        <set-body>@{
                try {
                    var responseBody = context.Response.Body.As<JObject>(preserveContent: true);

                    // Transforming response body if the field exists
                    if (responseBody["output_content"] != null) {
                        responseBody["inference"] = responseBody["output_content"].ToString();
                        responseBody.Remove("output_content");
                    }

                    return responseBody.ToString();
                }
                catch (Exception ex) {
                    return JObject.FromObject(new { error = "Invalid JSON format in response body." }).ToString();
                }
            }</set-body>
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
```

次にお風呂機器の専門家Agentのポリシーを設定します。
- Request Body の role フィールドを、type に変換。content フィールドを、message に変換
- Response Body の result フィールドを、inference に変換。
```xml
<policies>
    <inbound>
        <base />
        <set-backend-service id="apim-generated-policy" backend-id="agenticworld-agents-api" />
        <set-body>@{
                var bodyString = context.Request.Body.As<string>(preserveContent: true);
                JObject requestBody = null;

                try
                {
                    requestBody = Newtonsoft.Json.JsonConvert.DeserializeObject<JObject>(bodyString);

                    // Transforming request body if the field exists
                    if (requestBody["messages"] != null)
                    {
                        foreach (var message in requestBody["messages"].Children<JObject>())
                        {
                            message["type"] = message["role"];
                            message["message"] = message["content"];
                            message.Remove("role");
                            message.Remove("content");
                        }
                    }
                }
                catch (Exception ex)
                {
                    return Newtonsoft.Json.JsonConvert.SerializeObject(new { error = "Invalid JSON format in request body.", details = ex.Message });
                }

                return requestBody.ToString();
            }</set-body>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
        <set-body>@{
                var responseBody = context.Response.Body.As<JObject>(preserveContent: true);

                // Transforming response body if the field exists
                if (responseBody["result"] != null)
                {
                    responseBody["inference"] = responseBody["result"]["message"].ToString();
                    responseBody.Remove("result");
                }

                return responseBody.ToString();
            }</set-body>
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
```

これで、オーケストレーターからはそれぞれの専門家Agentを同じAPIルールで呼び出せるようになりました。

## 6. Azure Functions の Durable Functions を使ったAgentオーケストレーションの作成
再掲ですが、このようなワークフローをDurable Functionsで作成します。
![](/images/agentic-world-api-management/2025-01-12-00-40-29.png)

Durable Functionsにはいくつかのアプリケーションパターンがあります。今回はFan out/Fan inパターンで実装します。
https://learn.microsoft.com/ja-jp/azure/azure-functions/durable/durable-functions-overview?tabs=in-process%2Cnodejs-v3%2Cv1-model&pivots=csharp#fan-in-out

必要な関数はこれらです。
- アクティビティ関数
  - 専門家AgentのAPIを呼び出す関数
- オーケストレーター関数
  - ここで上記の図のワークフローを定義します。
- クライアント関数
  - オーケストレーター関数を呼び出す関数

### アクティビティ関数

```python
@myApp.activity_trigger(input_name="params")
def call_qa_agents(params: str):
    """
    QAエージェントAPIを呼び出すアクティビティ関数。

    パラメータ:
    params (str): JSON形式の文字列で、QAエージェントAPIに必要なパラメータを含む。

    戻り値:
    str: QAエージェントAPIのレスポンスボディ
    """
    try:
        return post_qa_agents_api(params)
    except Exception as e:
        logging.error(e)
        return f"Error: {e}"

def post_qa_agents_api(params: str):
    """
    指定されたURLに対してPOSTリクエストを送信する関数。

    パラメータ:
    params (str): JSON形式の文字列で、以下のキーを含む必要がある。
        - subscription_key: APIのサブスクリプションキー
        - post_url: POSTリクエストを送信するURL
        - post_params: POSTリクエストのパラメータ（辞書形式）

    戻り値:
    str: POSTリクエストのレスポンスボディ
    """

    try:
        # Jsonにする
        params_json = json.loads(params)
        logging.info(f"  params_json: {params_json}")

        # POSTする
        subscription_key = params_json["subscription_key"]
        post_params = params_json["post_params"]  # ここでは辞書として保持する

        headers = {
            "subscription-key": subscription_key,
            "Ocp-Apim-Subscription-Key": Ocp_Apim_Subscription_Key
        }

        result = requests.post(
            params_json["post_url"],
            json=post_params,  # 辞書型をそのまま渡す
            headers=headers
        )

        # エンコーディングをUTF-8に設定
        result.encoding = 'utf-8'

        # POSTで返却されたBodyを返す
        logging.info(f"  result: {result.text}")
        return result.text

    except Exception as e:
        logging.error(e)
        raise e
```

### オーケストレーター関数

```python
@myApp.orchestration_trigger(context_name="context")
def agents_orchestrator(context: df.DurableOrchestrationContext):
    """
    複数のQAエージェントAPIを呼び出し、その結果をタスク管理エージェントAPIに渡すオーケストレーター関数。

    パラメータ:
    context (df.DurableOrchestrationContext): オーケストレーションコンテキスト

    戻り値:
    str: タスク管理エージェントAPIのレスポンスボディ
    """

    try:
        params = context.get_input()

        if not params:
            raise ValueError("No parameters provided")

        # params.agentsの数だけ、call_qa_agentsを呼び出す
        qa_agents_task = []
        for agent in params["agents"]:
            # agentをstringにして渡す
            qa_agents_task.append(context.call_activity(
                "call_qa_agents", json.dumps(agent)))

        # qa_agentsの結果を待つ
        results = yield context.task_all(qa_agents_task)

        logging.info("各専門家からの結果を取得しました。")

        # resultsリストの文字列を結合
        answer_str = ""
        for result in results:
            result_dict = json.loads(result)  # ここでJSONとしてパース
            if "inference" in result_dict:
                answer_str += result_dict["inference"] + "\n\n"

        logging.info(f" answer_str: {answer_str}")

        # qa_agentsの結果を使い、call_taskmanagement_agentを呼び出す
        taskmanagement_result = yield context.call_activity("call_taskmanagement_agent", answer_str)

        logging.info(f" taskmanagement_result: {taskmanagement_result}")

        return taskmanagement_result

    except Exception as e:
        logging.error(e)
        return f"Error: {e}"
```

### クライアント関数

```python
@myApp.route(route="orchestrators/{functionName}")
@myApp.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    """
    HTTPリクエストをトリガーとしてオーケストレーションを開始する関数。

    パラメータ:
    req (func.HttpRequest): HTTPリクエストオブジェクト
    starter (str): オーケストレーションを開始するためのスターター

    戻り値:
    func.HttpResponse: HTTPレスポンスオブジェクト
    """
    try:
        function_name = req.route_params.get('functionName')

        # Bodyのparamsを取得し、Orchestratorを起動する
        params = req.get_json()
        logging.info(f"params: {params}")

        instance_id = await client.start_new(function_name, None, params)
        response = client.create_check_status_response(req, instance_id)
        return response

    except Exception as e:
        logging.error(e)
        return func.HttpResponse(f"Error: {e}", status_code=500)
```

## 7. 動作確認
Durable Functionsのクライアント関数をRestAPIで呼び出し、動作確認します。**実装したワークフローで実行**されています。
::: message
※Durable Functionsに開発において、フローがどのように実行されたかが追いにくいことが難点です。PrivatePreviewである、Durable Task Schedulerを使うと、UIから実行ログを追うことができるようになるため、PublicPreviewを心待ちにしています！
:::
https://youtu.be/fbGcqRQ8Cxc

**API Managementのログ**を見ると、各専門家Agentが実行されたことが分かります。
![](/images/agentic-world-api-management/2025-01-12-10-23-56.png)

**Functionsのログ**で、各RequestBodyのパラメータがどうなっているか確認しましょう。APIManagementの変換ポリシーにより、専門家ごとに異なるパラメータ名に変換されているはずです。
**空調機器の専門家Agent**のログです。このAgentはAPIルール通りなのでそのままですね。
![](/images/agentic-world-api-management/2025-01-12-10-28-36.png)

次に**キッチン機器の専門家Agent**のログです。APIルールと異なるパラメータ名に変換されていることが分かります。
![](/images/agentic-world-api-management/2025-01-12-10-29-28.png)

**お風呂機器の専門家Agent**のログです。こちらもAPIルールと異なるパラメータ名に変換されていることが分かります。
![](/images/agentic-world-api-management/2025-01-12-10-30-03.png)


# まとめ
Azure FunctionsとAPI Managementを使って、専門家Agentをオーケストレーションする方法を紹介しました。
今回はAPIManagementを使ったAPI管理に焦点を置きました。
マルチエージェントの仕組みを個々に開発することは、各開発チームの裁量で可能ですが、仕事の自動化という点では組織全体でどう進めるのかが大切だと思っています。
そういう点だと、組織としてエージェント開発を推進する際には、各専門家Agentを開発する環境の整備（プラットフォームエンジニアリング）なども必要になります。