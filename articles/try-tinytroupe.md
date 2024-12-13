---
title: "【TinyTroupe🤠🤓🥸🧐】マルチエージェント ペルソナシミュレーションツール！？"
emoji: "👪"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["LLM", "TinyTroupe", "Azure", "OpenAI", "MultiAgent"]
published: true
---

::: message
[Azure PoC部 Advent Calendar 2024 - Adventar](https://adventar.org/calendars/10622) 13日目の記事です。
:::

# はじめに
LLMが登場してから、役割や実行することが異なる複数のAIエージェントを組み合わせる、マルチエージェントシステムが注目されています。Microsoft Ignite 2024でも、マルチエージェントに関わるセッションが多く開催されました。

マルチエージェントシステムについて、たまたまMicrosoftのGitHubのリポジトリに面白そうなマルチエージェントペルソナシミュレーションがありましたので、興味本位でお試ししてみます。

![](/images/try-tinytroupe/2024-12-07-17-33-16.png)
※本画像はGitHubリポジトリより引用 <https://github.com/microsoft/TinyTroupe>

Microsoft Ignite 2024ではトヨタ自動車がマルチエージェントシステム"O-beya"を発表しました。
https://news.microsoft.com/ja-jp/features/241120-toyota-is-deploying-ai-agents-to-harness-the-collective-wisdom-of-engineers-and-innovate-faster/?msockid=2ded0802190e6e23183c1d4318536fb4
https://devblogs.microsoft.com/cosmosdb/toyota-motor-corporation-innovates-design-development-with-multi-agent-ai-system-and-cosmos-db/
AutoGenなどのマルチエージェントのフレームワークは、AI任せでカスタマイズが難しく、業務利用するには難しいと思っていました。
O-beyaはDurableFunctionsを使い、AIの組み合わせとワークフローが実装できることが強みですね。

この記事で紹介するTinyTroupeは、AutoGenやO-beyaなどとは目的が異なるツールのようです。
"シミュレーションツール"という位置づけです。実装レベルでカスタマイズはできそうにないので、"ツール"と呼ばせていただきます。

# TinyTroupe🤠🤓🥸🧐とは？？？
端的に言うと、実際の人間をLLMで模擬したシミュレーションツールです。
🤠🤓🥸🧐とあるように、さまざまな人格を模擬するイメージです。

GitHubのREADMEには以下のように記載されています。
- **特定の性格、興味、目標を持つ人々のシミュレーションを可能にする実験的な Python ライブラリ**

ユースケースは以下のように考えられています。
- デジタル広告を、仮想のユーザで評価する
- ITシステムのソフトウェアテストにて、仮想のユーザがテスト入力し結果を評価する
- 機械学習のための仮想的なデータセットを生成する
- 製品やプロジェクトに対し、仮想のペルソナからのフィードバックを提供する

::: message
TinyTroupe自体、研究プロジェクトで開発中です。
本記事は2024/12/07時点の情報ですので、最新の情報はGitHubリポジトリをご確認ください。
https://github.com/microsoft/TinyTroupe
:::

## 人格と世界の概念
主に二つの概念があります。TinyPersonとTinyWorldです。
- **TinyPerson**
  - 人格、興味、目標を持つAIエージェント。
  - シミュレーションを通り、外部からの刺激に対してアクションします。アクションにはいくつか種類があります。
  listen、see、act、listen_and_act
  - 各エージェントの作成方法は3つ。
    - TinyTroupeで事前用意されたエージェント
    - 手動ですべて定義：TinyPerson()でエージェントを作成し、define()で人格を定義します。
    - LLMを使って指示に応じたエージェントを生成：TinyPersonFactory()を使ってエージェントを生成します。
- **TinyWorld**
  - 複数のエージェント（TinyPerson）が存在する世界。
  - TinyPersonを複数指定し、シミュレーション環境を作成します。

### TinyPersonFactoryを使った人格生成
TinyPersonFactoryを使って、TinyPersonを生成できます。
```python
financial_specialist = factory.generate_person(
  """
  金融のスペシャリスト。銀行業務、投資、資産運用に精通しており、金融市場の動向を常に把握している。
  新しい金融商品やサービスの開発に携わっており、特にテクノロジーを活用した金融イノベーションに関心がある。
  日本の金融業界の発展に貢献することを目指している。
  """
)
```

生成した人格は、Json形式でファイル出力可能です。実際に上記で生成された人格を出力してみます。
```python
financial_specialist.save_spec("./try/brainstorm_auto_traits/financial_specialist.json")
```

出力されたJsonはこちら。名前、年齢、国籍、居住国、職業、ルーティン、性格、興味、スキル、関係、現在の状態などが記載されています。
このままの人格でシミュレーションしてもよいですし、このJsonファイルを修正して、JsonファイルからTinyPersonを生成することもできます。
```json
{
    "json_serializable_class_name": "TinyPerson",
    "_configuration": {
        "name": "Akira Yamamoto",
        "age": 40,
        "nationality": "Japanese",
        "country_of_residence": "Japan",
        "occupation": "Financial Specialist",
        "routines": [
            {
                "routine": "Every morning, you start your day with a cup of green tea while reviewing the latest financial news before heading to the office."
            },
            {
                "routine": "During lunch breaks, you often meet with colleagues to discuss market insights and potential investment strategies."
            },
            {
                "routine": "In the evenings, you dedicate time to researching emerging financial technologies and trends."
            }
        ],
        "occupation_description": "You are a financial specialist with extensive experience in banking, investment, and asset management. You work for a leading financial institution in Tokyo, where you analyze market trends and develop innovative financial products. Your role involves collaborating with technology teams to integrate cutting-edge solutions into traditional financial services, aiming to enhance customer experience and operational efficiency. You are passionate about contributing to the evolution of Japan's financial industry, but you often feel the pressure of meeting high expectations from your superiors.",
        "personality_traits": [
            {
                "trait": "You are analytical and detail-oriented, often diving deep into data to uncover insights."
            },
            {
                "trait": "You can be somewhat reserved, preferring to listen rather than dominate conversations."
            },
            {
                "trait": "You have a strong sense of responsibility and often feel the weight of your decisions."
            },
            {
                "trait": "You are optimistic about the future of finance, but sometimes struggle with self-doubt regarding your ideas."
            }
        ],
        "professional_interests": [
            {
                "interest": "You are particularly interested in fintech innovations and how they can disrupt traditional banking."
            },
            {
                "interest": "You enjoy exploring sustainable investment opportunities and their impact on society."
            },
            {
                "interest": "You are keen on networking with other professionals in the financial sector to share knowledge and ideas."
            }
        ],
        "personal_interests": [
            {
                "interest": "You enjoy playing chess, as it sharpens your strategic thinking."
            },
            {
                "interest": "You have a passion for photography, often capturing urban landscapes and financial districts."
            },
            {
                "interest": "You like to attend art exhibitions, finding inspiration in the creativity of others."
            }
        ],
        "skills": [
            {
                "skill": "You are proficient in financial modeling and analysis, using tools like Excel and specialized software."
            },
            {
                "skill": "You have strong communication skills, allowing you to present complex ideas clearly."
            },
            {
                "skill": "You are adept at using data visualization tools to convey financial information effectively."
            }
        ],
        "relationships": [
            {
                "name": "Yuki",
                "description": "your supportive spouse, who works in marketing and often provides you with a different perspective on your ideas."
            },
            {
                "name": "Taro",
                "description": "your mentor from your early career, who continues to guide you in your professional journey."
            }
        ],
        "current_datetime": null,
        "current_location": "Tokyo, Japan",
        "current_context": [],
        "current_attention": null,
        "current_goals": [],
        "current_emotions": "I feel a mix of excitement and anxiety about the future of the financial industry.",
        "current_memory_context": null,
        "currently_accessible_agents": []
    },
    "_mental_faculties": [],
    "name": "Akira Yamamoto"
}
```

## シミュレーションの開始時の指示
シミュレーションの開始前に、議論/行動してほしいことを依頼する方法はいくつかあります。
- **tinyworldのbroadcast**：全員にメッセージを送信します。
- **tinyworldのbroadcast_internal_goal**：全員に目標を与えます。
- **tinypersonのlisten()**：最初に一人のTinyPersonにメッセージを送信します。その人から会話が始まります。

ブレインストームのような、全員に共通認識を与えたい場合はbroadcastでよいと思います。
特定の人に指示をして開始したい場合には、tinypersonのlisten()を使います。

## シミュレーションの開始
TinyWorldには、いくつかのシミュレーション実行モードがあります。
- **run**：会話を何回繰り返すかを指定します。
- **run_days**：指定した日数だけ実行します。
- **run_hours**：指定した時間だけ実行します。
- **run_minutes**：指定した分数だけ実行します。
- **run_months**：指定した月数だけ実行します。
- **run_weeks**：指定した週数だけ実行します。
- **run_years**：指定した年数だけ実行します。


## その他のUtility
他にも便利なUtilityが用意されています。これら以外にもあります。
- **TinyPersonFactory**：LLMでTinyPerson（人格、興味、目標など）を生成します。
- **TinyTool**
- **TinyStory**：シミュレーションのストーリーの作成/管理
- **TinyPersonValidator**：TinyPersonの動作検証
- **ResultsExtractor**：エージェント間の対話結果を抽出できます。

## キャッシュ機能
過去のシミュレーションを途中から開始するために、キャッシュ機能があります。シミュレーションを9回進めたあと、10回目のシミュレーションにいくつかのパターンがある場合、1-9回目は再実行したくありません。LLM呼び出しのコストがかかってしまいます。

キャッシュの種類は２つあります。
**１つ目はシミュレーション状態のキャッシュです**。
- シミュレーションの状態変更の記録を開始し、ファイルへの保存を開始します。
```python
control.begin("<CACHE_FILE_NAME>.cache.json")
```
- その時のシミュレーション状態を保存します。
```python
control.checkpoint()
```
- control.begin()によって開始されたシミュレーション記録スコープを終了します。
```python
control.end()
```

**２つ目はLLMのAPI呼び出しのキャッシュです**。
LLMへの問い合わせをキャッシュし、新しい問い合わせが過去の問い合わせと同じである場合、キャッシュした応答をそのまま返します。
config.iniで有効化するか、実行時にopenai_utils.force_api_cache()を呼び出します。

# 動かすための事前準備です

## 環境変数と設定ファイル
環境変数を設定します。
「.env.local」にAzureOpenAIのエンドポイントとAPIキーを設定します。
```bash
AZURE_OPENAI_KEY=AzureOpenAIのAPIキー
AZURE_OPENAI_ENDPOINT=AzureOpenAIのエンドポイント
```

examplesフォルダにあるconfig.iniを修正します。
- API_TYPEを「azure」に変更
- AZURE_API_VERSIONを「2024-10-01」に変更　※2024/12/07時点の最新バージョン

デフォルトで、gpt-4o-miniとtext-embedding-3-smallが使うように設定されています。
もちろん、AzureOpenAIに必要なモデルをデプロイしておきましょう。


# それでは動作させていきましょう。
examplesにはAnacondaの環境で実行するためのJupyter Notebookが用意されています。
今回は理解を深めるために自分で実装していきます。

まずは必要なライブラリをインポートします。
```python
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import ResultsExtractor

from dotenv import load_dotenv
import json

load_dotenv()
```

つぎにシミュレーションのための人格（TinyPerson）を設定します。今回は人格をLLMで生成させます。
AIエンジニア、金融のスペシャリスト、自動車業界の会長の3人を生成します。
生成した人格はJsonファイルに保存します。
```python
factory = TinyPersonFactory("新しい日本の産業を生み出すためのワークショップ")
ai_engineer = factory.generate_person(
  """
  AIエンジニア。機械学習と生成AIを組み合わせて、企業向けのAIツールを開発及び展開している。
  エンドユーザの課題を見つけ出し、AIを活用して解決することに注力している。
  """
)
financial_specialist = factory.generate_person(
  """
  金融のスペシャリスト。銀行業務、投資、資産運用に精通しており、金融市場の動向を常に把握している。
  新しい金融商品やサービスの開発に携わっており、特にテクノロジーを活用した金融イノベーションに関心がある。
  日本の金融業界の発展に貢献することを目指している。
  """
)
automotive_chairman = factory.generate_person(
  """
  自動車業界の会長。自動車産業における豊富な経験と知識を持ち、業界の発展と革新に尽力している。
  新しい技術やサービスの導入を推進し、グローバルな視点で自動車業界の未来を見据えている。
  """
)

ai_engineer.save_spec("./try/brainstorm_auto_traits/ai_engineer.json")
financial_specialist.save_spec("./try/brainstorm_auto_traits/financial_specialist.json")
automotive_chairman.save_spec("./try/brainstorm_auto_traits/automotive_chairman.json")
```

つぎにシミュレーションしたい環境（TinyWorld）を作成し、実行します。
```python
world = TinyWorld("Meeting Room", [ai_engineer, financial_specialist, automotive_chairman])
world.make_everyone_accessible()

instruct = '''
新しい世界的なサービスを生み出すためのワークショップです。
自由な発想で新たなサービスを考え、議論してください！！！
'''

world.broadcast(instruct)

world.run(10)
```



会話のサマリーはこちら
```json
{
  "summary": {
    "workshop": "The agents participated in a workshop aimed at brainstorming innovative ideas for a new global service.",
    "key_ideas": [
      {
        "idea": "Sustainable Investment Strategies",
        "details": "Akira proposed creating a global service focused on sustainable investment strategies to align financial goals with ethical practices."
      },
      {
        "idea": "Real-time Financial Advice Platform",
        "details": "Akira also suggested developing a platform that provides real-time financial advice using AI technology to enhance customer experience."
      },
      {
        "idea": "Integration of Electric Vehicle Services",
        "details": "Takeshi proposed integrating electric vehicle services with smart city infrastructure to enhance user experience and promote sustainability."
      },
      {
        "idea": "Mobile App for Charging Stations",
        "details": "Takeshi suggested developing a mobile app that connects users with charging stations in real-time, providing information on availability and pricing."
      },
      {
        "idea": "Partnerships with Renewable Energy Providers",
        "details": "Takeshi emphasized exploring partnerships with renewable energy providers to offer bundled services for electric vehicle owners."
      },
      {
        "idea": "Financial Literacy Service",
        "details": "Akira proposed creating a financial literacy service to help individuals understand their finances better, especially in emerging markets."
      }
    ],
    "discussion_points": [
      {
        "point": "AI Integration",
        "details": "The agents discussed how AI could optimize energy consumption and enhance user experience across their proposed services."
      },
      {
        "point": "Marketing Strategy",
        "details": "They emphasized the importance of tailoring their marketing strategy for emerging markets and considering partnerships with local organizations."
      },
      {
        "point": "Presentation Preparation",
        "details": "The agents focused on preparing a compelling presentation that highlights the benefits of their integrated services, including effective data visualization and addressing potential stakeholder questions."
      }
    ]
  }
}
```

会話ログはこちら
https://github.com/nomhiro/TinyTroupe/blob/main/try/brainstorm_auto_traits/%E4%BC%9A%E8%A9%B1%E3%83%AD%E3%82%B0.txt


# まとめ
様々なパターンで動かしてみましたが、**「どのような人格を設定するか」と「人格設定のプロンプト」が非常に重要**です。シミュレーションのために必要そうな人格を指定する必要があるので、シミュレーションのための役割が不足していると会話が収束していきません。
また、シミュレーション中の会話を見ながら、人がエージェントに指示を出せるため、試すならAnacondaのJupyter Notebookで実行するのが良いです。
"AIエージェント"という言葉がはやりですが、こういったシミュレーションツールという観点での新しいアプローチのツールで面白いですね。