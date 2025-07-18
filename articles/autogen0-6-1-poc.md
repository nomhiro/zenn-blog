---
title: "AutoGen (0.6.1) の基本的な構成要素"
emoji: "🔖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["AutoGen", "AI", "LLM"]
published: true
---

![](/images/autogen0-6-1-poc/2025-06-11-22-17-06.png)

単一のAIは、色々な質問に答えてくれて便利ですが、以下のような限界があります。

- **専門知識の限界**: 非常に専門的な分野や、複数の分野にまたがる複雑な問題では、単一のAIだけでは対応しきれないことがあります。
- **情報の整合性**: 間違った情報（ハルシネーション）を出力したり、事実と異なることを言ってしまうこともあります。
- **多様な視点の欠如**: 一つの視点からの回答になりがちで、様々な角度からの意見を統合することが難しいです。
まるで一人の人間が、あらゆる専門知識を網羅し、常に完璧な答えを出すのが難しいのと同じですね。そこで登場するのが、それぞれの専門分野を持ったAIたちが協力し合うマルチエージェントAIシステムです。

AutoGenは、複数のAIエージェントが協力し合い、専門家チームのように連携してタスクを解決するフレームワークです。

1年前にもAutoGenを使ったPoCをしましたが、当時はバージョン0.2でした。
https://zenn.dev/nomhiro/articles/autogen-abstract
最近Autogen 0.6.1 になったので、改めて基本的な構成要素を整理します。

---

## AutoGenとは？

AutoGenは、複数のAIエージェントが連携して複雑なタスクを解決するためのフレームワークです。人間のチームのようにそれぞれの専門家（エージェント）が協力し、対話しながら問題を解決していきます。これにより、単一のAIでは難しい高度なタスクも効率的にこなせるようになります。

---

AutoGenの主要な構成要素と機能はこれらです。
- **エージェント (Agents)**
- **チーム (Teams)**
- **人間の介入 (Human-in-the-Loop)**
- **終了条件 (Termination)**
- **状態管理 (State Management)**

他にも、メモリとRAGについてや、ログ、Studioなどもありますが、この記事では割愛します。


### 1. エージェント (Agents)

エージェントはAutoGenのベースとなる構成要素です。それぞれのエージェントは特定の役割や能力を持ち、互いにメッセージを送り合って対話します。

- **`AssistantAgent`**: AIモデル（ChatGPTなど）の能力を活用して、ユーザーの指示や他のエージェントからのメッセージに基づいて応答を生成します。コードの生成や情報のリサーチなど、様々なタスクを実行できます。

他にも、いくつかのエージェントが用意されています。
- **`UserProxyAgent`**: 人間ユーザーの代理として振る舞うエージェントです。ユーザーからの入力やフィードバックをAIエージェントに伝えたり、AIエージェントが生成したコードを実行したりする役割を担います。これにより、AIが生成したコードの検証や、人間による介入が可能になります。
- **`CodeExecutorAgentt`**: コードを実行できるエージェントです。
OpenAIAssistantAgent: OpenAIのAssistant APIをバックエンドとして使用し、カスタムツールも使えるエージェントです。
- **`MultimodalWebSurfert`**: ウェブを検索し、ウェブページにアクセスしてマルチモーダルな情報（画像やテキストなど）を収集できるエージェントです。
- **`FileSurfert`**: ローカルファイルを検索し、閲覧して情報を収集できるエージェントです。
- **`VideoSurfert`**: ビデオを視聴して情報を収集できるエージェントです。

だだし、AIに求める振る舞いがこれら用意されているエージェントでは対応できない場合もあるかもしれませんね？
そういう場合は、「**カスタムエージェント**」です。
- 独自のロジック実装: 例えば、数字を数えたり、特定の計算をしたりする、シンプルなエージェントを作成できます。
- 未サポートのモデル利用: AutoGenが標準で対応していない新しいAIモデルを、カスタムエージェント内で直接利用できます。これにより、最新のAI技術を柔軟に組み込むことが可能です。

---

### 2. チーム (Teams)

AutoGenでは、複数のエージェントを組み合わせてチームを形成し、より複雑な問題を解決できます。チーム内のエージェントは互いに協力し、情報を共有しながら目標達成を目指します。

AgentChatには、以下の事前構成済みチームがあります。

- **RoundRobinGroupChat**
  - 参加者が順番に発言するラウンドロビン方式でグループチャットを実行します。エージェントが交互にタスクを進めるようなシナリオで役立ちます。

- **SelectorGroupChat**
  - 各メッセージの後、次に発言するエージェントを選択します。対話の状況に応じて最適なエージェントが自動的に選ばれるため、より柔軟な会話が行われます。

- **MagenticOneGroupChat**
  - オープンエンドなWebベースのタスクやファイルベースのタスクを、様々な知識ドメインで解決するための汎用的なマルチエージェントシステムです。多様な情報ソースから知識を集め、複雑な問題を解決するのに向いています。

- **Swarm**
  - HandoffMessageを使用してエージェント間の遷移をシグナルするチームです。特定のタスクの完了後、次のエージェントにスムーズに引き継ぎを行うような、ワークフローベースのタスクに適しています。

---

### 3. 人間の介入 (Human-in-the-Loop)

Human-in-the-Loopとは、AIの処理プロセスに人間が介在し、フィードバックしたり、意思決定を行ったりする仕組みです。これにより、AIのパフォーマンスを向上させたり、AIでは判断できない状況で適切な指示を与えられます。

AutoGenのチームとやり取りする方法は、主に2つあります。

1. **チームの実行中**：実行中の状態に対してフィードバックを提供します。
2. **実行終了後**：次の呼び出しへの入力としてフィードバックを提供します。


---

### 4. 終了条件 (Termination)

エージェントの会話は放っておくと永遠に続いてしまう可能性があります。そこで重要になるのが、「終了条件 (Termination Condition)」の役割です。

終了条件は呼び出し可能な関数です。この関数は、前回の呼び出し以降に生成されたメッセージのシーケンスを受け取り、会話を終了すべきであればStopMessageを返し、そうでなければNoneを返します。
AND演算子やOR演算子を使って組み合わせることができます。これにより、複数の条件を組み合わせて、より複雑な終了ロジックを構築できます。

:::message
グループチャットチーム（例：RoundRobinGroupChat、SelectorGroupChat、Swarm）の場合、終了条件は各エージェントが応答した後に呼び出されます。応答には複数の内部メッセージが含まれることがありますが、チームはその単一の応答からのすべてのメッセージに対して終了条件を一度だけ呼び出します。
:::

組み込み終了条件がいくつか用意されています。

- **MaxMessageTermination**
エージェントとタスクメッセージの両方を含む、指定されたメッセージ数が生成された後に停止します。例えば、「3往復の会話で終了する」といった設定が可能です。

- **TextMentionTermination**
  - メッセージ内で特定のテキストや文字列が言及されたときに停止します（例：「TERMINATE」という単語が検出されたら終了）。これは、エージェントに会話の終了を指示する際に非常によく使われます。

- **TokenUsageTermination**
  - プロンプトまたは完了トークンの使用量が指定された数に達したときに停止します。エージェントがトークン使用量を報告する必要がありますが、コスト管理に役立ちます。

- **TimeoutTermination**
  - 指定された秒数（継続時間）が経過した後に停止します。AIエージェントが無限ループに陥るのを防ぐのに役立ちます。

- **HandoffTermination**
  - 特定のエージェント（またはユーザー）へのハンドオフが要求されたときに停止します。これは、Swarmのようなパターンを構築するのに使えます。エージェントがユーザーに引き継いだ際に、アプリケーションやユーザーが入力できるように実行を一時停止したい場合に便利です。

- **SourceMatchTermination**
  - 特定のソースエージェントが応答した後に停止します。

- **ExternalTermination**
  - 実行の外部からプログラム的に終了を制御できます。チャットインターフェースの「停止」ボタンなど、UIとの統合に非常に役立ちます。

- **StopMessageTermination**  
  - エージェントによってStopMessageが生成されたときに停止します。

- **TextMessageTermination**
  - エージェントによってTextMessageが生成されたときに停止します。

- **FunctionCallTermination** 
  - エージェントによって、一致する名前を持つFunctionExecutionResultを含むToolCallExecutionEventが生成されたときに停止します。

- **FunctionalTermination**
  - メッセージの最後のデルタシーケンスで、関数式がTrueと評価されたときに停止します。組み込みの終了条件ではカバーできない、カスタムの終了条件を素早く作成するのに便利です。

---

### 5. 状態管理 (State Management)

エージェントやチーム、そして終了条件の状態を保存し、後で読み戻すことができます。
セッションをまたいでAIエージェントとのやり取りを継続したり、アプリケーションが落ちた際に状態を復元したりできます。


* **状態の保存**: 会話の履歴やエージェントの内部状態（例えば、生成されたコードや中間結果）をファイル（JSON形式など）に保存できます。
* **状態のロード**: 保存された状態をロードすることで、中断した会話を再開したり、過去の会話を分析したりすることが可能です。

これにより、長時間のタスクや、途中で中断する可能性のあるタスクでも、柔軟に対応できるようになります。

```python
import autogen
import json

# エージェントの定義（上記と同様）
assistant = autogen.AssistantAgent(name="assistant")
user_proxy = autogen.UserProxyAgent(name="user_proxy")

# 会話の開始と状態の取得
user_proxy.initiate_chat(assistant, message="今日のニュースを要約してください。")
chat_history = user_proxy.chat_messages[assistant] # 会話履歴を取得

# 状態の保存
with open("chat_state.json", "w") as f:
    json.dump(chat_history, f, indent=4)

# 後で状態をロードして会話を再開する例（ここでは実行しませんが概念として）
# with open("chat_state.json", "r") as f:
#     loaded_chat_history = json.load(f)
# user_proxy.initiate_chat(assistant, message="続きを教えてください。", default_auto_reply=loaded_chat_history)
```

---

## まとめ

AutoGen は、エージェント、チーム、人間の介入、終了条件、そして状態管理といった強力な機能を組み合わせることで、複雑なAIアプリケーションを効率的に開発できるフレームワークです。

次は、具体例と実装例とともに振る舞いを確認していきます。