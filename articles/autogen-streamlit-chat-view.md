---
title: "AutoGenの会話をWebアプリ（Streamlit）上に表示しよう！！"
emoji: "🙋"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["AutoGen", "Streamlit", "LLM", "AI", "Agent"]
published: true
---

![](/images/autogen-streamlit-chat-view/2025-07-21-22-51-00.png)

# はじめに
AIエージェントとマルチエージェントシステムをPoCしています。
考え方（観点）と知識を持っている各エージェントが連携し、より高度なタスクの実行やアイデア出しやブラッシュアップをしてほしいです。

そこで、AutoGenを使ったマルチエージェントシステムをPoCしていました。
当初は単にAIエージェント同士が議論する様子をコンソールで眺めていただけでした。
![](/images/autogen-streamlit-chat-view/2025-07-21-10-52-18.png)

これではUI的に微妙なのと、並列に複数のエージェントが議論する様子を可視化したいと思い、Streamlitで非同期にAIエージェント同士のチャットの様子を可視化することにしました。

こちらのGitHubで公開しています。
https://github.com/nomhiro/synapse-map

::: message alert
AutoGenは、Semantic Kernelに統合される予定があるようです。
そのため、今後はSemantic Kernelを使うことが推奨されるかもしれません。
https://devblogs.microsoft.com/semantic-kernel/semantic-kernel-and-autogen-part-2/
:::

::: message
ちなみに、MCP（Model Control Protocol）を複数用意して、単一エージェントでタスクを実行することもできますが、今回は異なる考え方や観点を持つエージェント同士の会話が必要だと思ったので、AutoGenでのマルチエージェントにしました。
:::

# 先に結論

こんな感じになりました。
- オンデマンドでAutoGenによるマルチエージェントの会話を実行（非同期処理）
- 実行終了、実行中の会話を確認できるセッション一覧
- セッションごとに、AIエージェント同士の会話を可視化

https://youtu.be/riaKDAVPWmk


# システム構成とアーキテクチャ

アーキテクチャはこちらです。

![](/images/autogen-streamlit-chat-view/2025-07-21-12-05-13.png)

- **Web UI （Streamlit）**
  - Web UIフレームワークとしては、簡易PoC版ですのでStreamlitを使ってます。
  - ただし、Streamlitには制約もあります。特に非同期処理との相性は良くないため、工夫が必要でした（これについては後述します）。
- **AutoGen**
  - AutoGenは、AIエージェント同士の会話を実現するためのフレームワークです。各エージェントは異なる知識や観点を持ち、協力してタスクを遂行します。
  - AutoGenについてはこちらで簡単に解説しています。
  https://zenn.dev/nomhiro/articles/autogen0-6-1-poc
- **Cosmos DB**
  - 会話の履歴やセッション情報を保存するために、Cosmos DBを使用しています
  - Cosmos DBは、スケーラブルで高可用性のデータベースサービスで、非同期処理にも適しています。


# システムの動作フロー

実際にユーザーがブレインストーミングを開始してから結果を得るまでの流れを追ってみましょう。

## 1. タスク入力とセッション開始

```python
# StreamlitのUIでタスク入力
task = st.text_area("検討したいアイデア・課題を入力してください")

if st.button("🚀 ブレインストーミング開始"):
    # AutoGenランナーを使ってセッション開始
    runner = get_runner()
    session_id = runner.start_session_async(task)
```

ここでポイントなのは`start_session_async`です。Streamlitのメインスレッドをブロックしないよう、別スレッドでAutoGenセッションを実行します。

## 2. エージェント間の議論

セッションが開始されると、SessionManagerが司会役となって議論を進行します。

```python
async def run_team_chat(self, team, task):
    """チームでの会話を実行"""
    stream = team.run_stream(task=task)
    
    async for chunk in stream:
        if chunk.type == "TextMessage":
            # メッセージをリアルタイムで処理
            self.process_message(chunk)
```

各エージェントの発言は、即座にメッセージキューに追加され、UIに反映されます。

## 3. リアルタイム表示

Streamlit側では、定期的にメッセージキューをチェックして新しい発言を表示します。

```python
# 2秒ごとに画面を更新
if st.session_state.session_running:
    new_messages = runner.get_new_messages()
    st.session_state.live_messages.extend(new_messages)
    
    # メッセージを表示
    for message in st.session_state.live_messages:
        with st.chat_message(message['source']):
            st.markdown(message['content'])
    
    time.sleep(2)
    st.rerun()
```

## 4. データの永続化

各メッセージは、発言と同時にCosmosDBに保存されます。

```python
async def save_message_realtime(self, message_data):
    """メッセージをリアルタイムで保存"""
    message_doc = {
        "id": f"{self.session_id}_msg_{sequence}_{timestamp}",
        "session_id": self.session_id,
        "type": "message",
        "source": message_data["source"],
        "content": message_data["content"],
        "timestamp": message_data["timestamp"]
    }
    
    await self.container.create_item(message_doc)
```

# AutoGenの実装

GitHubに公開している状態のエージェントは、5つのエージェントがあります。
このブログと公開しているGitHubでは、各エージェントはRAGをしないエージェントです。（Azure OpenAI GPT-4.1に対して、システムプロンプトで役割定義して呼び出しているだけのエージェント）
各エージェントのtoolプロパティで、RAGツールやMCPなどと組み合わせることも可能ですので、独自知識を与えたい場合はRAGやMCPなどを組み合わせましょう。

1. **CreativePlanner（創造的企画者）**: アイデアの種を生み出す
2. **MarketAnalyst（市場分析者）**: 市場性と競合を分析
3. **TechnicalValidator（技術検証者）**: 実現可能性を検証
4. **BusinessEvaluator（事業評価者）**: ビジネス価値を評価
5. **UserAdvocate（ユーザー代弁者）**: ユーザー視点で検証

## エージェントの実装

### 基底クラスの設計

まず、すべてのエージェントが継承する基底クラスを作成しました。

```python
from abc import ABC, abstractmethod
from autogen_agentchat.agents import AssistantAgent

class BaseAgent(ABC):
    """エージェントの基底クラス"""
    
    @abstractmethod
    def get_name(self) -> str:
        """エージェント名を取得"""
        pass
    
    @abstractmethod
    def get_system_message(self) -> str:
        """システムメッセージを取得"""
        pass
    
    def create_agent(self, llm_config: dict) -> AssistantAgent:
        """AutoGenエージェントを作成"""
        return AssistantAgent(
            name=self.get_name(),
            system_message=self.get_system_message(),
            llm_config=llm_config
        )
```

この設計により、新しいエージェントの追加が簡単になります。

### エージェントの実装例

例として、CreativePlannerの実装はこちらです。

```python
class CreativePlannerAgent(BaseAgent):
    """創造的な企画者エージェント"""
    
    def get_name(self) -> str:
        return "creative_planner"
    
    def get_system_message(self) -> str:
        return """あなたは創造的なアイデアを生み出す専門家です。

役割：
- 既存の枠にとらわれない斬新な視点から提案を行う
- 異分野の知識を組み合わせて新しいコンセプトを創出する
- 「もし〜だったら」という仮説思考を活用する

アプローチ：
1. まず与えられた課題の本質を別の角度から捉え直す
2. 類似の成功事例を異業種から探し、応用可能性を検討する
3. 技術的制約を一旦無視して理想的なソリューションを描く
4. ユーザーの潜在的なニーズを想像力を使って掘り下げる

重要：
- 実現可能性よりもインパクトと新規性を重視する
- 他のエージェントの意見に刺激を受けて、さらに発展させる
- 「できない理由」ではなく「できる方法」を考える"""
```

システムメッセージの工夫点：
1. **明確な役割定義**: 何をすべきかが具体的
2. **アプローチの指針**: どのように考えるべきかを示す
3. **他エージェントとの協調**: 議論を発展させることを促す

## SelectorGroupChatによる議論の実現

### なぜSelectorGroupChatを使うのか

AutoGenには複数の会話パターンがありますが、SelectorGroupChatを選んだ理由は「動的な発言順序」です。

通常のRoundRobinでは発言順が固定されますが、実際のブレインストーミングでは、話の流れに応じて次の発言者が決まります。SelectorGroupChatはこれを再現できます。

### Selectorの実装

議論の司会者となるSelectorの設定が重要です。

```python
def _create_selector_prompt(self) -> str:
    return """あなたは議論の司会者です。
    
現在の議論状況を分析し、次に発言すべき最適なエージェントを選択してください。

選択の指針：
1. アイデア出しの初期段階
   → creative_planner（新しいアイデアが必要）
   
2. アイデアが出された直後
   → market_analyst（市場性の検証）
   → technical_validator（技術的実現性）
   
3. 基本的な検証が済んだ後
   → business_evaluator（ビジネス価値）
   → user_advocate（ユーザー視点）
   
4. 議論が煮詰まったとき
   → creative_planner（新しい切り口）

重要：
- 同じエージェントが連続で話さないように配慮
- すべてのエージェントが均等に発言機会を得られるように
- 議論の自然な流れを重視"""
```

この司会者の存在により、人間のファシリテーターのような役割をAIが担います。

## 終了条件の設計

### カスタム終了条件の実装

議論をいつ終了させるかは重要な問題です。単純な回数制限では、良い議論が途中で切れてしまうことがあります。

そこで、カスタムの終了条件を実装しました：

```python
class AgentCountTermination(TerminationCondition):
    """各エージェントの発言回数に基づく終了条件"""
    
    def __init__(self, max_count_per_agent: int = 3):
        self._max_count = max_count_per_agent
        self._agent_message_count = {}
    
    async def __call__(self, messages) -> bool:
        # 最新のメッセージを確認
        if messages:
            last_message = messages[-1]
            agent_name = last_message.source
            
            # システムメッセージは除外
            if agent_name not in ["user", "assistant", "system"]:
                self._agent_message_count[agent_name] = \
                    self._agent_message_count.get(agent_name, 0) + 1
            
            # すべてのエージェントが規定回数発言したら終了
            active_agents = [name for name, count in self._agent_message_count.items() 
                           if count >= self._max_count]
            
            if len(active_agents) >= 5:  # 5人全員が発言
                return True
        
        return False
```

この実装により、全員が十分に発言した時点で自然に議論が終了します。

## 実際の議論例

これらの設計がどのように機能するか、実際の議論例を見てみましょう：

```
タスク: 「リモートワーク時代の新しいコミュニケーションツール」

creative_planner: 「物理的な距離を感じさせない『空間共有型』のツールを提案します。
VRではなく、デスクトップ上に仮想オフィスを再現し、アバターが自然に動き回れる
2.5次元の空間です。雑談や偶発的な出会いを演出できます」

market_analyst: 「Gather.townやSpatialChatなど類似サービスは存在しますが、
日本市場での認知度はまだ低いです。特に日本企業の文化に合わせた
『席次』や『会議室予約』機能があれば差別化できるでしょう」

technical_validator: 「WebRTCとCanvas APIを使えば、ブラウザだけで実装可能です。
重要なのは低遅延での同期です。まずは10人規模から始めて、
段階的にスケールアップする approach が現実的でしょう」

business_evaluator: 「SaaSモデルで1ユーザー月額1,000円なら、
100社×20人で月商200万円。開発費用を考慮すると、
18ヶ月でブレークイーブンが見込めます」

user_advocate: 「リモートワークの最大の課題は『孤独感』です。
このツールが単なる会議ツールではなく、『つながり』を感じられる
場所になることが成功の鍵ですね」
```

各エージェントが前の発言を受けて、自分の専門性から付加価値を加えているのが分かります。

## エージェント設計のポイント

1. 専門性の明確化
   - 各エージェントの専門領域を明確にし、重複を避けることが重要です。曖昧な役割定義は、議論の質を下げる原因になります。

2. 協調性の組み込み
   - システムメッセージに「他のエージェントの意見を踏まえて」という指示を含めることで、議論が発展しやすくなります。

3. バランスの考慮
   - 批判的すぎるエージェントがいると議論が停滞し、楽観的すぎると現実味がなくなります。このバランスを取ることが、良い議論を生む秘訣です。


## SessionManagerの役割と実装

AutoGenのエージェントは強力ですが、単体では「会話の記録」「外部システムとの連携」「リアルタイム通知」といった機能は提供されません。SessionManagerは、これらの機能を統合的に管理する中枢的な役割を果たします。

### 核心となるメッセージフック機能

リアルタイム表示を実現する上で重要なのが、メッセージフックです。SessionManagerは、各エージェントからのメッセージを受け取り、CosmosDBやStreamlitのUIに通知します。

```python
class SessionManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.session_id = None
        self.message_hooks = []  # 外部通知用のフック
        self.cosmosdb_manager = None
        
    def add_message_hook(self, hook: Callable[[Dict[str, Any]], None]):
        """外部システムへの通知フックを追加"""
        self.message_hooks.append(hook)
    
    def _notify_message_hooks(self, message_data: Dict[str, Any]):
        """すべてのフックに新しいメッセージを通知"""
        for hook in self.message_hooks:
            try:
                hook(message_data)
            except Exception as e:
                safe_print(f"メッセージフック実行エラー: {e}")
```

このフック機能により、StreamlitのUIにメッセージを反映できます。

### エージェント作成と会話実行

各エージェントの作成から実際の会話実行までのフローを見てみましょう：

```python
def _create_team(self) -> SelectorGroupChat:
    """5つの専門エージェントとセレクターからなるチームを作成"""
    
    # LLM設定を統一
    llm_config = {
        "config_list": [
            {
                "model": self.settings.azure_openai_model,
                "api_type": "azure",
                "api_version": self.settings.azure_openai_api_version,
                "base_url": self.settings.azure_openai_endpoint,
                "api_key": self.settings.azure_openai_api_key,
            }
        ],
        "temperature": 0.7,
    }
    
    # 各専門エージェントを作成
    agents = [
        CreativePlannerAgent().create_agent(llm_config),
        MarketAnalystAgent().create_agent(llm_config),
        TechnicalValidatorAgent().create_agent(llm_config),
        BusinessEvaluatorAgent().create_agent(llm_config),
        UserAdvocateAgent().create_agent(llm_config)
    ]
    
    # 司会者エージェントを作成
    selector = AssistantAgent(
        name="selector",
        system_message=self._create_selector_prompt(),
        llm_config=llm_config,
    )
    
    # カスタム終了条件を設定
    termination = AgentCountTermination(max_count_per_agent=3)
    
    return SelectorGroupChat(
        participants=agents,
        model_client=selector,
        termination_condition=termination,
    )
```

### 会話実行とリアルタイム処理

実際の会話実行では、各メッセージをリアルタイムで処理します。

```python
async def run_team_chat(self, team, task):
    """チームでの会話を実行し、リアルタイムで処理"""
    try:
        # ストリーミング形式で会話を開始
        stream = team.run_stream(task=task)
        
        async for chunk in stream:
            if hasattr(chunk, 'type') and chunk.type == "TextMessage":
                # メッセージデータを構造化
                message_data = {
                    "source": chunk.source,
                    "content": chunk.content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "session_id": self.session_id
                }
                
                # 外部システムに即座に通知
                self._notify_message_hooks(message_data)
                
                # CosmosDBにリアルタイム保存
                if self.cosmosdb_manager:
                    await self.cosmosdb_manager.save_message_realtime(message_data)
                    
    except Exception as e:
        safe_print(f"チャット実行エラー: {e}")
        raise
```

## エージェント間の協調メカニズム

### SelectorGroupChatの仕組み

AutoGenのSelectorGroupChatは、動的にエージェントを選択して会話を進行します。ここで重要なのは司会者（Selector）の役割です。

```python
def _create_selector_prompt(self) -> str:
    return """あなたは議論の司会者です。
    
現在の議論状況を分析し、次に発言すべき最適なエージェントを選択してください。

選択の指針：
1. アイデア出しの初期段階
   → creative_planner（新しいアイデアが必要）
   
2. アイデアが出された直後
   → market_analyst（市場性の検証）
   → technical_validator（技術的実現性）
   
3. 基本的な検証が済んだ後
   → business_evaluator（ビジネス価値）
   → user_advocate（ユーザー視点）
   
4. 議論が煮詰まったとき
   → creative_planner（新しい切り口）

重要な原則：
- 同じエージェントが連続で話さないように配慮
- すべてのエージェントが均等に発言機会を得られるように
- 議論の自然な流れを最優先に考える

次に発言させるエージェント名のみを回答してください。"""
```

この司会者の存在により、人間のファシリテーターのような役割をAIが担い、議論が自然に進行します。

### 終了条件の実装詳細

議論をいつ終了させるかは、システムの品質を左右する重要な要素です。シンプルな回数制限ではなく、「全員が十分に発言した時点」で終了するカスタム条件を実装しました。
Yokohama-sanがブログを書いてくださったので詳細はこちらを参照してください！
https://blog.beachside.dev/entry/2025/07/17/083000

```python
class AgentCountTermination(TerminationCondition):
    """各エージェントの発言回数に基づく終了条件"""
    
    def __init__(self, max_count_per_agent: int = 3):
        self._max_count = max_count_per_agent
        self._agent_message_count = {}
    
    async def __call__(self, messages) -> bool:
        if not messages:
            return False
            
        # 最新のメッセージを確認
        last_message = messages[-1]
        agent_name = last_message.source
        
        # システムメッセージやユーザーメッセージは除外
        if agent_name not in ["user", "assistant", "system", "selector"]:
            # エージェントの発言回数をカウント
            self._agent_message_count[agent_name] = \
                self._agent_message_count.get(agent_name, 0) + 1
        
        # 規定回数発言したエージェントの数を確認
        active_agents = [
            name for name, count in self._agent_message_count.items() 
            if count >= self._max_count
        ]
        
        # 5人全員が規定回数発言したら終了
        if len(active_agents) >= 5:
            return True
        
        return False
```

# StreamlitとAutoGenの統合

AutoGenのマルチエージェントシステムをStreamlitのWebUIと統合するときに、いくつかの課題がありました。

1. 非同期処理とStreamlitの相性問題
   - Streamlitは基本的に同期的な処理モデルで設計されており、AutoGenの非同期処理と直接組み合わせるのは困難でした。AutoGenのセッションが実行中にStreamlitのメインスレッドがブロックされると、UIが応答しなくなってしまいます。
2. リアルタイム更新の実現
   - 議論の進行をリアルタイムで表示するには、バックグラウンドで進行するAutoGenセッションの状況を、StreamlitのUIに反映する仕組みが必要でした。
3. 状態管理の複雑さ
   - 複数のページ間での状態共有、セッションの開始・停止制御、エラーハンドリングなど、Webアプリケーションとしての堅牢性が求められました。

## StreamlitAutoGenRunnerの設計

これらの課題に対処するために、専用のクラス`StreamlitAutoGenRunner`を実装しました。

キューを使うことで、スレッド間でのメッセージ受け渡しを安全に行えます。
```python
import threading
import queue
from typing import Dict, Any, List, Optional, Callable

class StreamlitAutoGenRunner:
    def __init__(self):
        self.session_manager = None
        self.message_queue = queue.Queue()
        self.session_thread = None
        self.is_running = False
        self.current_session_id = None
        self.session_complete = False
        
    def _message_hook(self, message_data: Dict[str, Any]):
        """SessionManagerからのメッセージを受信してキューに追加"""
        self.message_queue.put(message_data)
```

### 非同期セッション実行

AutoGenセッションを別スレッドで実行し、メインスレッドをブロックしないような実装です。

```python
def start_session_async(self, task: str, callback: Optional[Callable] = None) -> str:
    """AutoGenセッションを非同期で開始"""
    if self.is_running:
        raise RuntimeError("セッションは既に実行中です")
    
    # セッションIDを生成
    self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    self.is_running = True
    self.session_complete = False
    
    # 別スレッドでセッションを実行
    self.session_thread = threading.Thread(
        target=self._run_session_in_thread,
        args=(task, callback),
        daemon=True  # メインプロセス終了時に自動的に終了
    )
    self.session_thread.start()
    
    return self.current_session_id

def _run_session_in_thread(self, task: str, callback: Optional[Callable] = None):
    """スレッド内でAutoGenセッションを実行"""
    try:
        # 設定読み込み
        settings = Settings.from_env()
        
        # SessionManagerを作成してフックを追加
        self.session_manager = SessionManager(settings)
        self.session_manager.add_message_hook(self._message_hook)
        
        # セッション実行（非同期）
        asyncio.run(self.session_manager.run_chat_session(
            session_id=self.current_session_id,
            task=task
        ))
        
        # 完了通知
        self.session_complete = True
        if callback:
            callback()
            
    except Exception as e:
        # エラー情報をキューに送信
        error_message = {
            "source": "system",
            "content": f"エラーが発生しました: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "error"
        }
        self.message_queue.put(error_message)
        
    finally:
        self.is_running = False
```

UIに表示するメッセージを効率的に取得する実装です。

```python
def get_new_messages(self) -> List[Dict[str, Any]]:
    """新しいメッセージを全て取得（ノンブロッキング）"""
    messages = []
    
    try:
        # キューから利用可能なメッセージを全て取得
        while True:
            message = self.message_queue.get_nowait()
            messages.append(message)
    except queue.Empty:
        # キューが空になったら終了
        pass
    
    return messages

def get_session_status(self) -> Dict[str, Any]:
    """現在のセッション状況を取得"""
    return {
        "is_running": self.is_running,
        "session_id": self.current_session_id,
        "session_complete": self.session_complete,
        "queue_size": self.message_queue.qsize()
    }
```

# CosmosDB連携（データ保管）

AIエージェントの議論をリアルタイムで保存します。また、今までのセッション履歴を永続的に保管し、後から確認できるようにします。

## パーティションキー設計

CosmosDBで最も重要なのがパーティションキーの設計です。
セッション単位でのデータ取得が最も頻繁であるため、セッションIDをパーティションキーとすることにしました。


### データ構造設計

```python
# セッション情報ドキュメント
session_document = {
    "id": "session_20240120_143022",
    "session_id": "session_20240120_143022",  # パーティションキー
    "type": "session_info",
    "task": "リモートワーク時代の新しいコミュニケーションツール",
    "created_at": "2024-01-20T14:30:22.123456",
    "status": "completed",
    "message_count": 15,
    "participants": ["creative_planner", "market_analyst", "technical_validator", "business_evaluator", "user_advocate"]
}

# メッセージドキュメント
message_document = {
    "id": "session_20240120_143022_msg_0001_1705737022123456",
    "session_id": "session_20240120_143022",  # パーティションキー
    "type": "message",
    "source": "creative_planner",
    "content": "物理的な距離を感じさせない『空間共有型』のツールを提案します...",
    "timestamp": "2024-01-20T14:30:25.123456",
    "sequence": 1
}
```

# まとめ
本記事では、AutoGenとStreamlitを組み合わせたマルチエージェントシステムの実装について、アーキテクチャ設計から実装の詳細まで幅広く解説しました。

AutoGenでは、SelectorGroupChatによる動的な会話制御にすることで、固定的な発言順序ではなく、議論の流れに応じて次の発言者を選択することで、より自然で建設的な議論となります。

技術的に困ったのは、Streamlitの同期処理とAutoGenの非同期処理を統合することでしたが、専用のRunnerクラスとメッセージキューを使ったスレッド間通信により、メインスレッドをブロックすることなくリアルタイム更新することができました。

UI/UX面でも、より直感的な議論の可視化や、ユーザーが議論に参加できる機能など、改善の余地は多くあります。AutoGenのSemantic Kernelへの統合予定もあり、今後のマルチエージェントシステムの発展が非常に楽しみです。
また、マルチエージェントの必要性と、MCPツールかによるシングルエージェントの使い分けも重要になってきそうです。