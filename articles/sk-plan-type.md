---
title: "PythonにおけるSemanticKernelのPlannerの種類を整理する"
emoji: "📝"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["SemanticKernel", "Planner"]
published: false
---

# はじめに
SemanticKernelをまだまだ使いこなせてませんが、AOAIのドーナツ本を読む中で、Plannerの種類がいくつかあることを知りました。そのため、Plannerの種類を整理してみます。
ここではPythonで使えるPlannerを試します。
C#版ではいくつかPlannerに変更があったようなので、そちらについては別途調査します。[Migrating from the Sequential and Stepwise planners to the new Handlebars and Stepwise planner](https://devblogs.microsoft.com/semantic-kernel/migrating-from-the-sequential-and-stepwise-planners-to-the-new-handlebars-and-stepwise-planner/)

## そもそもSemanticKernelとは
SemanticKernelは、CopilotStackのAIオーケストレーション層に位置する、開発フレームワークです。[What is Semantic Kernel?](https://learn.microsoft.com/en-us/semantic-kernel/overview/)
SemanticKernelには主に以下の機能があります。
- 複数のLLMを一緒に利用できる。
- 個々の機能をプラグイン化して、プラグインを使って目標を達成する実行計画を立てられる。
- メモリー機能を使って、アプリケーションが保持したい内容をEmbeddingした状態で保持できる。

※CopilotStackはMicrosotが提示した、LLMを利用しプラグインや外部システムと連携して、MicrosoftのCopilot製品や独自のCopilotを開発するときにフレームワークです。
![CopilotStack](/images/sk-plan-type/2024-02-02-22-32-44.png)

## Plannerの種類
Plannerには、現在以下の4つの種類が使えるようです。
- BasicPlanner
- ActionPlanner
- SequentialPlanner
- StepwisePlanner

それぞれ、どのような特徴があるのかを調べてみます。
実際に試した際のプログラムは[こちらのGitHub](https://github.com/nomhiro/sk-plan-type-samplecode)にあります。
実行する際には、.envファイルを作成し以下のように設定してください。
```env
AZURE_OPENAI_API_KEY="{AzureOpenAIのAPIキー}"
AZURE_OPENAI_ENDPOINT="{AzureOpenAIのエンドポイント}"
AZURE_OPENAI_DEPLOYMENT_NAME="{AzureOpenAIのデプロイ名}"
```


### 1.BasicPlanner
BasicPlannerは、プラグインのリストとゴールを受け取り、**プラグインを順番に実行**するプランを作成します。確かにBasicだなと。

実際に試してみます。
与える目標は、「**文章にタイトルをつけて、そのタイトルをフランス語にしてもらうこと**」です。
以下のような動きになってくれるはずです。
![BasicPlanner](/images/sk-plan-type/2024-02-03-12-02-27.png)

こちらが実際に試したPythonコードです。

```python
ask = """以下の文章にタイトルをつけて。タイトルはフランス語にしてほしい。

AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。
セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。"""

# プラグインの読み込み
plugins_directory = "./plugins/"
summarize_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "SummarizePlugin")
writer_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "WriterPlugin")
text_plugin = kernel.import_plugin(TextPlugin(), "TextPlugin")

planner = BasicPlanner()
# プランの生成
basic_plan = await planner.create_plan(ask, kernel)
print("### generated plan ###")
print(basic_plan.generated_plan)

# プランの実行
results = await planner.execute_plan(basic_plan, kernel)
print("\n\n### results ###")
print(results)
```

実行すると以下のような実行計画が得られました。想定通りの実行計画です。
実行計画を立てるときには、プラグインの名前と、そのプラグインに渡す引数が表示されています。"input"は、SummarisePlugin.MakeTitleの引数になっています。WritePlugin.Translateの引数には、一つ前のサブタスクの結果が渡されます。
```json
### generated plan ###
{
    "input": "AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。",
    "subtasks": [
        {"function": "SummarizePlugin.MakeTitle"},
        {"function": "WriterPlugin.Translate", "args": {"language": "French"}}
    ]
}
```

このプランを実行すると以下の結果が得られました。フランス語でタイトルがつけられていて、日本語訳すると「AIエージェントの構築とセマンティック・カーネル」のようなので想定通りの結果です。
```
### results ###
Construction d'agent IA et noyau sémantique
```

### 2.ActionPlanner
ActionPlannerは、プラグインのリストとゴールを受け取り、**そのゴールを達成するために適切なプラグインを1つ出力**する。
BasicPlannerでは複数のプラグインが組み合わせられて実行計画が立てられましたが、こちらは1つだけ選ばれることが特徴です。OpenAIのFunctionCallingに似てますね。

実際に試してみます。
タスクを一つ実行するプランナーなので、与える目標は、「**文章にタイトルをつけて**」とします。（後ほどBasicPlannerのときのように、複数の目標を与えるとどうなるのか、挙動確認してみます。）
以下のような動きになってくれるはずです。
![actionPlanner](/images/sk-plan-type/2024-02-03-12-03-51.png)


こちらが実際に試したPythonコードです。

```python
ask = """以下の文章にタイトルをつけて。

AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。
セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。"""

# プラグインの読み込み
plugins_directory = "./plugins/"
summarize_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "SummarizePlugin")
writer_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "WriterPlugin")

# ActionPlannerのインスタンスを生成
planner = ActionPlanner(kernel)
# プランの生成
action_plan = await planner.create_plan(goal=ask)
print("### generated plan ###")
print(f"plugin_name: {action_plan.plugin_name} / {action_plan.name}")

# プランの実行
results = await action_plan.invoke()
print("\n\n### results ###")
print(results)
```

BasicPlannerと実装上の違いがいくつかあります。
- ActionPlannerのインスタンスを生成する際にKernelを指定し、create_planの引数にgoalを渡しています。
- 生成されたプランも、BasicPlannerの時のようにJson形式で返されるのではなく、選択された一つのプラグインの名前が返されます。
- プラン実行の仕方も異なり、invokeメソッドを使います。

実行すると以下のような実行計画が得られました。想定通りに、SummarizePluginのMakeTitleが選ばれていることがわかります。
```
### generated plan ###
plugin_name: SummarizePlugin / MakeTitle
```

このプランを実行すると以下の結果が得られます。こちらも想定通りの結果です。
```
### results ###
AIモデルとコード統合の自動化
```

#### ActionPlannerで複数の目標を与えるとどうなるのか
ActionPlannerでは一つの関数のみを選択するためのPlannerですが、BasicPlannerのときのように、複数の目標を与えるとどうなるのか、挙動確認してみます。

与える目標は、BasicPlannerの時と同じで「**文章にタイトルをつけて、そのタイトルをフランス語にしてもらうこと**」です。

実際に試したPythonコードです。
askの内容を変更しただけで、ほかのコードはActionPlannerの挙動確認時と同じです。
```python
ask = """以下の文章にタイトルをつけて。タイトルはフランス語にしてほしい。

AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。
セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。"""

# プラグインの読み込み
plugins_directory = "./plugins/"
summarize_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "SummarizePlugin")
writer_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "WriterPlugin")

# ActionPlannerのインスタンスを生成
planner = ActionPlanner(kernel)
# プランの生成
action_plan = await planner.create_plan(goal=ask)
print("### generated plan ###")
print(f"plugin_name: {action_plan.plugin_name} / {action_plan.name}")

# プランの実行
results = await action_plan.invoke()
print("\n\n### results ###")
print(results)
```

実行すると、Plannerの生成時にエラーが発生しました。
```
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/runpy.py", line 198, in _run_module_as_main
    return _run_code(code, main_globals, None,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/runpy.py", line 88, in _run_code
    exec(code, run_globals)
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/__main__.py", line 39, in <module>
    cli.main()
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/../debugpy/server/cli.py", line 430, in main
    run()
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher/../../debugpy/../debugpy/server/cli.py", line 284, in run_file
    runpy.run_path(target, run_name="__main__")
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 321, in run_path
    return _run_module_code(code, init_globals, run_name,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 135, in _run_module_code
    _run_code(code, mod_globals, init_globals,
  File "/home/vscode/.vscode-server/extensions/ms-python.debugpy-2024.0.0-linux-x64/bundled/libs/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_runpy.py", line 124, in _run_code
    exec(code, run_globals)
  File "/workspaces/sk-plan-type-samplecode/actionPlanner.py", line 54, in <module>
    asyncio.run(main())
  File "/usr/local/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/asyncio/base_events.py", line 684, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/workspaces/sk-plan-type-samplecode/actionPlanner.py", line 45, in main
    action_plan = await planner.create_plan(goal=ask)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspaces/sk-plan-type-samplecode/.venv/lib/python3.12/site-packages/semantic_kernel/planning/action_planner/action_planner.py", line 142, in create_plan
    plugin, fun = generated_plan["plan"]["function"].split(".")
    ^^^^^^^^^^^
ValueError: too many values to unpack (expected 2)
```

SemanticKernelライブラリの内部処理を詳細に追えてはいませんが、ライブラリ内の以下のコードでsplit(".")の結果が2つ以上の要素を持ってしまい、pluginとfunの2つの変数にアンパックできないことが原因のようです。一つの目標しか与えられない前提のPlannerになっているようです。
```python
plugin, fun = generated_plan["plan"]["function"].split(".")
```

### 3.SequentialPlanner
SequentialPlannerは、一連のステップを実行し、ステップ間で出力と入力を受け渡すことができるプランナーです。
BasicPlannerと似てますが、XMLベースなので作成したプランを保存して再利用することができることが利点だと思います。[公式ページ](https://learn.microsoft.com/ja-jp/semantic-kernel/agents/planners/?tabs=python#using-predefined-plans)にもそのような記載がありますね。
また、作成されたプランを変更することもできるようです。
:::message
- アプリケーションで活用しようとした場合、頻繁に実行される決まったプランを保存しておいて再利用することができるので、再利用性が高いという利点があります。
- また、作成されたプランをユーザに表示し、ユーザにプランのレビュー（プラン自体やステップの入力データを変更）をしたうえで実行できます。
:::
:::message alert
2023年Igniteあたりの時期に、C#のSemanticKernelではSequentialPlannerからHandlebarsPlannerに移行したようです。SemanticKernelはC#がメインで開発されていますが、いずれPythonでもHandlebarsPlannerに移行するのかもしれません。
[Migrating from the Sequential and Stepwise planners to the new Handlebars and Stepwise planner](https://devblogs.microsoft.com/semantic-kernel/migrating-from-the-sequential-and-stepwise-planners-to-the-new-handlebars-and-stepwise-planner/)
:::

実際に試してみます。
与える目標はBasicPlannerの時と同様で、「**文章にタイトルをつけて、そのタイトルをフランス語にしてもらうこと**」です。
以下のような動きになってくれるはずです。
![sequentialPlanner](/images/sk-plan-type/2024-02-03-12-02-27.png)

こちらが実際に試したPythonコードです。

```python
ask = """以下の文章にタイトルをつけて。タイトルはフランス語にしてほしい。

AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。
セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。"""

# プラグインの読み込み
plugins_directory = "./plugins/"
summarize_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "SummarizePlugin")
writer_plugin = kernel.import_semantic_plugin_from_directory(plugins_directory, "WriterPlugin")

# ActionPlannerのインスタンスを生成
planner = SequentialPlanner(kernel)
# プランの生成
sequential_plan = await planner.create_plan(goal=ask)
print("### generated plan ###")
for step in sequential_plan._steps:
    print("■ step: ", sequential_plan._steps.index(step) + 1, "/", len(sequential_plan._steps))
    print(step.description, ": ", step._state.__dict__)
    print("input: ", step._parameters.input)

# プランの実行
results = await sequential_plan.invoke()
print("\n\n### results ###")
print(results)
```

実行すると以下のような実行計画が得られました。想定通りに、SummarizePluginのMakeTitleとTranslateが選ばれていることがわかります。
```
### generated plan ###
■ step:  1 / 2
文章にタイトルをつける。 :  {'variables': {'input': ''}}
input:  AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。 セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。
■ step:  2 / 2
Translate the input into a language of your choice :  {'variables': {'input': ''}}
input:  $title
```

このプランを実行すると以下の結果が得られます。こちらも想定通りの結果です。
```
### results ###
Construction d'agent IA et noyau sémantique
```

### 4.StepwisePlanner
最後にStepwisePlannerです。StepwisePlannerは、AIが「思考」と「観察」を行い、ユーザーの目標を達成するための行動を実行します。必要な機能がすべて完了し、最終的な出力が生成されるまで続けられます。

実際に試してみます。
与える目標はBasicPlannerの時と同様で、「**文章にタイトルをつけて、そのタイトルをフランス語にしてもらうこと**」です。

以下のような実行計画になってくれるはずです。
![StepwisePlanner](/images/sk-plan-type/2024-02-03-12-02-27.png)

こちらが実際に試したPythonコードです。

```python
ask = """以下の文章にタイトルをつけて。タイトルはフランス語にしてほしい。

AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。
セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。"""

# ActionPlannerのインスタンスを生成
planner = StepwisePlanner(kernel, StepwisePlannerConfig(max_iterations=10, min_iteration_time_ms=1000))
# プランの生成
stepwise_plan = planner.create_plan(goal=ask)

print("### generated plan ###")
for index, step in enumerate(stepwise_plan._steps):
    print("Step:", index)
    print("Description:", step.description)
    print("Function:", step.plugin_name + "." + step._function.name)

# プランの実行
results = await stepwise_plan.invoke()
print("\n\n### results ###")
print(results)
```

実行するとSummarizePlugin.Summarize、WriterPlugin.Translate、およびSummarizePlugin.MakeTitleの3つのステップが計画されました。想定とは異なりましたが、問題なさそうです。
- [THOUGHT]というステップがありますが、これはStepwisePlannerの思考にあたりますね。
- 次に[ACTION]で実行する関数と引数が表示されています。
- 最後に[OBSERVATION]が観察で、このステップでの結果が表示されています。
このように計画された3つのステップが順番に実行され、最終的な結果が得られます。
```
### see steps ###
Step: 0
Description: Execute a plan
Function: StepwisePlanner.ExecutePlan
  Output:
 This was my previous work (but they haven't seen any of it! They only see what I return as final answer):
  [THOUGHT]
  まず、文章を要約し、その要約を元にタイトルを作成する必要があります。その後、そのタイトルをフランス語に翻訳します。これらのステップを実行するために、SummarizePlugin.Summarize、WriterPlugin.Translate、およびSummarizePlugin.MakeTitleの3つの関数を使用します。
  [ACTION]
  {"action": "SummarizePlugin.Summarize", "action_variables": {"input": "AIモデルは、ユーザー向けのメッセージや画像を簡単に生成できます。これは、シンプルなチャットアプリを構築する際には役立ちますが、ビジネスプロセスを自動化し、ユーザーがより多くのことを達成できるようにする、完全に自動化されたAIエージェントを構築するだけでは十分ではありません。そのためには、これらのモデルから応答を受け取り、それらを使用して既存のコードを呼び出し、実際に生産的なことを実行できるフレームワークが必要です。
セマンティックカーネルでは、まさにそれを実現しました。既存のコードを AI モデルに簡単に記述して、AI モデルが呼び出しを要求できるようにする SDK を作成しました。その後、セマンティック カーネルは、モデルの応答をコードの呼び出しに変換するという面倒な作業を行います。"}}
  [OBSERVATION]
  AIモデルはメッセージや画像の生成に役立つが、完全な自動化には不十分です。セマンティックカーネルは、AIモデルが既存のコードを呼び出すためのフレームワークを作成し、モデルの応答をコードの呼び出しに変換します。
  [THOUGHT]
  None
```

最終結果は以下のようになりました。想定通りの結果です。
```
### results ###
"Les modèles IA pour générer des messages et des images"
```


# まとめ
SemanticKernelのPythonで扱えるすべてのPlannerを調査しました。
各Plannerで特徴が異なるため、どのような用途で使うかで使い分けることになりそうです。
- プラグインを一つ選びたい。→ActionPlanner（OpenAIのFunctionCallingでもいいが）
- プランを保存して再利用したい。→SequentialPlanner
- プランを立てる際の思考を知りたい。→StepwisePlanner

C#のSemanticKernelでは、いくつかのPlannerに変更があったようなので、Pythonでもそのうち変更があるかもしれません。
C#版のPlannerについても調査してみようと思います。