---
title: "AI Foundry Browser Automation Tool で定常業務を自動化してみよう！"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "aifoundry", "llm", "openai", "playwright"]
published: true
---

# はじめに
Azure AI Foundry に、Browser Automation Tool の機能が追加されました。(まだPreviewです)
これにより、AIがブラウザ操作することができるため、**定常業務の自動化エージェント**が作成できそうと思ったので試してみます。

Browser Automationの超概要です。
- 自然言語でLLMがブラウザの操作可能
- Playwrightなので、「ダウンパース」手法により、Web ページの構造（DOM やアクセシビリティツリー）を解析。座標や画像認識に頼らず、要素を特定して操作できる。
- AzureのPlaywright Workspacesを使うことで、クラウド上で隔離された安全なブラウザー自動化環境が使えます。※VMなどが不要
- LLMを介すので、チャットのマルチターンで会話しながらブラウザ操作の可能。


https://devblogs.microsoft.com/a/announcing-the-browser-automation-tool-preview-in-azure-ai-foundry-agent-service/
https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/how-to/tools/browser-automation-samples
https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-foundry/agents/how-to/tools/browser-automation-samples.md

今回のブログでは、**日々の会話のメモをもとに、出張申請フォームに情報を入力して申請処理を自動化するエージェントを作成する**。というシナリオを想定して試してみます。

このような申請フォームです！
![](/images/browser-automation-ai-foundry-poc/2025-08-15-01-38-34.png)

# リソースの設定
これらのリソースの設定が必要です。
- PlayWright workspaces
- AI Foundry プロジェクト
  - PlayWright workspacesとの接続設定
  - モデルデプロイ
- 権限設定

## Playwright Workspace
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-43-54.png)

![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-44-58.png)

作成したPlaywright Workspaceで、アクセストークンを有効にします。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-46-37.png)

アクセストークンを生成して、生成されたトークンをコピーして控えておきます。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-47-29.png)

「概要」ページで、ワークスペース リージョン エンドポイントをコピーして控えておきます。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-48-49.png)


## AI Foundry の設定
プロジェクトを作成します。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-54-40.png)

![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-55-41.png)

作成したプロジェクト下で、管理センターの画面からConnected resourceを作成します。
※Playwright Workspaceへの接続設定です。

サーバーレスモデルをクリックします。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-58-43.png)

コピーしておいたPlaywright Workspaceのアクセストークンとリージョンエンドポイントを入力します。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-22-59-28.png)

## 権限設定
Playwright Workspaceに対して、プロジェクトIDに共同作成者の権限を付与します。
![](/images/browser-automation-ai-foundry-poc/2025-08-14-23-01-57.png)  


# 実装
Pythonで実装していきます。

まずは必要なライブラリをインストールします。
```bash
pip install azure-ai-agents>=1.2.0b2 azure-ai-projects azure-identity
```

.envを設定します。
```
PROJECT_ENDPOINT=AIFoundryのプロジェクトエンドポイント
PLAYWRIGHT_CONNECTION_NAME=AIFoundryで設定したConnected resourceの名前
MODEL_DEPLOYMENT_NAME=gpt-4.1
```

::: message alert
モデルですが、GPT-5はbrowser_automation typeがサポートされていないのか、エラーになります。今回はgpt-4.1を使います。
:::

Pythonコードです。

- LLMへのシステムメッセージ
    ```txt
    あなたは、ユーザから与えられた情報をもとに、出張申請フォームに情報を入力して申請処理を自動化するエージェントです。
    出張申請フォームのURL：https://witty-rock-0686e0000.2.azurestaticapps.net/

    ## ルール
    - ブラウザの操作はtoolsを使ってください。
    ```
- ユーザメッセージ
SlackやTeamsなどに出張に関する情報をコピーして、エージェントに申請を依頼するシーンを想定しています。
    ```txt
    対象者：しろくま
    日付：2025/08/14-2025/08/15
    行先：東京オフィス
    目的：XX案件での面着打合せ。
    備考：前泊予定。
    費用概算：30000円
    ```


```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from azure.ai.projects import AIProjectClient

project_endpoint = os.environ["PROJECT_ENDPOINT"]  # Ensure the PROJECT_ENDPOINT environment variable is set

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)

playwright_connection = project_client.connections.get(
    name=os.environ["PLAYWRIGHT_CONNECTION_NAME"]
)
print(playwright_connection.id)

with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"], 
        name="my-agent", 
        instructions="""あなたは、ユーザから与えられた情報をもとに、出張申請フォームに情報を入力して申請処理を自動化するエージェントです。
            出張申請フォームのURL：https://witty-rock-0686e0000.2.azurestaticapps.net/
            
            ## ルール
            - ブラウザの操作はtoolsを使ってください。""",
        tools=[{
            "type": "browser_automation",
            "browser_automation": {
            "connection": {
                "id": playwright_connection.id,
            }
        }
        }],
    )

    print(f"Created agent, ID: {agent.id}")

    thread = project_client.agents.threads.create()
    print(f"Created thread and run, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.messages.create(
        thread_id=thread.id, 
        role="user", 
        content="""対象者：しろくま
            日付：2025/08/14-2025/08/15
            行先：東京オフィス
            目的：XX案件での面着打合せ。前泊予定。
            費用概算：30000円""")
    print(f"Created message: {message['id']}")

    # Create and process an Agent run in thread with tools
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id, 
        agent_id=agent.id,
        )
    print(f"Run created, ID: {run.id}")
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(step)
        print(f"Step {step['id']} status: {step['status']}")

        # Check if there are tool calls in the step details
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                function_details = call.get("function", {})
                if function_details:
                    print(f"    Function name: {function_details.get('name')}")
        print()  # add an extra newline between steps

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    response_message = project_client.agents.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
    if response_message:
        for text_message in response_message.text_messages:
            print(f"Agent response: {text_message.text.value}")
        for annotation in response_message.url_citation_annotations:
            print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")
```

**実行結果はこちらです。**
問題なく動いてますね。単発エージェントとして動かすなら、申請に必要なコンテキストが十分Inputできているかが大事ですね。
1. まず、browser-automationが使えるAgentが作成。
2. thread、messageが作成され、LLMによるPlaywrightを使ったブラウザ操作が実行。
3. LLMが、Playwrightのツールを使って、ブラウザを操作し、出張申請フォームに情報を入力
4. フォームをSubmitして申請
```bash
vscode ➜ /workspaces/browser-automation (main) $  cd /workspaces/browser-automation ; /usr/bin/env /usr/local/bin/python /home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.10.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher 47721 -- /workspaces/browser-automation/.devcontainer/poc-analyze-oldcar.py 
/subscriptions/605923aa-f343-4a7d-b44f-c4599c81e059/resourceGroups/rg-browser-automation-poc/providers/Microsoft.CognitiveServices/accounts/browser-automation-agen-resource/projects/browser-automation-agent-poc/connections/playwright-automation-connection
Created agent, ID: asst_zKfo9H6LUtmpnslPWUCpPAuw
Created thread and run, ID: thread_8T0kgUa9py2HKqLvtjjIaMgX
Created message: msg_HMQdG3waSOppPlySItJofYVA
Run created, ID: run_HGVyrJFfJknQHW9kSje1qLRY
Run finished with status: RunStatus.COMPLETED
{'id': 'step_7lt0goNnRziRpctfIW4Tuncc', 'object': 'thread.run.step', 'created_at': 1755184042, 'run_id': 'run_HGVyrJFfJknQHW9kSje1qLRY', 'assistant_id': 'asst_zKfo9H6LUtmpnslPWUCpPAuw', 'thread_id': 'thread_8T0kgUa9py2HKqLvtjjIaMgX', 'type': 'message_creation', 'status': 'completed', 'cancelled_at': None, 'completed_at': 1755184043, 'expires_at': None, 'failed_at': None, 'last_error': None, 'step_details': {'type': 'message_creation', 'message_creation': {'message_id': 'msg_82ocL4ITxEQ8PDwXNntiB4Lu'}}, 'usage': {'prompt_tokens': 805, 'completion_tokens': 136, 'total_tokens': 941, 'prompt_token_details': {'cached_tokens': 0}}}
Step step_7lt0goNnRziRpctfIW4Tuncc status: completed

{'id': 'step_Zjli55GkkIRVliNSqS8E5gAb', 'object': 'thread.run.step', 'created_at': 1755183992, 'run_id': 'run_HGVyrJFfJknQHW9kSje1qLRY', 'assistant_id': 'asst_zKfo9H6LUtmpnslPWUCpPAuw', 'thread_id': 'thread_8T0kgUa9py2HKqLvtjjIaMgX', 'type': 'tool_calls', 'status': 'completed', 'cancelled_at': None, 'completed_at': 1755184042, 'expires_at': None, 'failed_at': None, 'last_error': None, 'step_details': {'type': 'tool_calls', 'tool_calls': [{'id': 'call_oQLq7fMI7lopQV8T7cBWODFV', 'type': 'browser_automation', 'browser_automation': {'input': 'Go to https://witty-rock-0686e0000.2.azurestaticapps.net/ and fill out the business trip application form with the following information:\n- å¯¾è±¡è\x80\x85ï¼\x9aã\x81\x97ã\x82\x8dã\x81\x8fã\x81¾\n- æ\x97¥ä»\x98ï¼\x9a2025/08/14-2025/08/15\n- è¡\x8cå\x85\x88ï¼\x9aæ\x9d±äº¬ã\x82ªã\x83\x95ã\x82£ã\x82¹\n- ç\x9b®ç\x9a\x84ï¼\x9aXXæ¡\x88ä»¶ã\x81§ã\x81®é\x9d¢ç\x9d\x80æ\x89\x93å\x90\x88ã\x81\x9bã\x80\x82å\x89\x8dæ³\x8aäº\x88å®\x9aã\x80\x82\n- è²»ç\x94¨æ¦\x82ç®\x97ï¼\x9a30000å\x86\x86\nThen, submit the form.', 'output': 'The business trip application form at https://witty-rock-0686e0000.2.azurestaticapps.net/ was filled out and submitted with the following information:\n- 件名 (Title): 出張申請\n- 対象者 (申請者): しろくま\n- 日付: 2025/08/14-2025/08/15\n- 行先: 東京オフィス\n- 目的: XX案件での面着打合せ。前泊予定。\n- 概算金額: 30000円\nSubmission was successful and confirmed by a registration message on the page. Ultimate task complete.', 'steps': [{'last_step_result': 'Unknown - The browser has just started and is displaying a blank page. No progress has been made yet towards the task.', 'current_state': 'Browser started. No steps towards the ultimate task have been completed. Need to navigate to the target URL to begin form filling. 0 out of 1 forms visited and filled. Task details for memory: Target site is https://witty-rock-0686e0000.2.azurestaticapps.net/, need to fill the business trip application form with the provided info and submit.', 'next_step': 'Navigate to https://witty-rock-0686e0000.2.azurestaticapps.net/ to access the business trip application form.'}, {'last_step_result': 'Success - Navigated to the target URL and the business trip application form is visible. All relevant input fields for the task are present in the viewport.', 'current_state': 'Navigated to https://witty-rock-0686e0000.2.azurestaticapps.net/. The business trip application form is now open and ready for input. 0 out of 1 forms filled and submitted. Need to input 対象者 (申請者): しろくま, 日付: 2025/08/14-2025/08/15 (startDate/endDate), 行先: 東京オフィス, 目的: XX案件での面着打合せ。前泊予定。, and 概算金額: 30000円. Final step is to submit the form.', 'next_step': 'Fill in the form fields with the task’s required information: 申請者 (index 5): しろくま, 開始日 (index 7): 2025-08-14, 終了日 (index 9): 2025-08-15, 訪問先 / 行先 (index 11): 東京オフィス, 目的 (index 13): XX案件での面着打合せ。前泊予定。, 概算金額 (index 17): 30000. Then submit the form.'}, {'last_step_result': 'Success - All required fields of the form were filled with the correct information as specified in the task: しろくま, 2025-08-14, 2025-08-15, 東京オフィス, XX案件での面着打合せ。前泊予定。, and 30000. The next step is to submit the form.', 'current_state': "All form fields have been correctly filled: applicant 'しろくま', start date '2025-08-14', end date '2025-08-15', destination '東京オフィス', purpose 'XX案件での面着打合せ。前泊予定。', estimated cost '30000'. Need to submit the form. 0 out of 1 forms submitted.", 'next_step': "Submit the filled business trip application form by clicking the '申請する' (Submit) button at index 20."}, {'last_step_result': 'Failed - The form failed to submit because the 件名 (title) field was left blank. An error message prompts to fill out this required field.', 'current_state': 'Business trip application form almost filled. Submission failed due to missing value for 件名 (title) at index 3. Need to enter a value for the title field before resubmitting. All other fields are correctly filled per instructions. 0 out of 1 forms successfully submitted.', 'next_step': "Input a reasonable 件名 (title) for the form, such as '出張申請', into index 3, then submit the form again."}, {'last_step_result': "Success - The form was correctly filled and submitted, shown by the confirmation message '申請を登録しました (ブラウザ保存)。' appearing on the page. All required fields match the provided task information.", 'current_state': 'Business trip application form at https://witty-rock-0686e0000.2.azurestaticapps.net/ filled with: 件名: 出張申請, 申請者: しろくま, 開始日: 2025-08-14, 終了日: 2025-08-15, 訪問先 / 行先: 東京オフィス, 目的: XX案件での面着打合せ。前泊予定。, 概算金額: 30000. Form was submitted and confirmation appeared. Ultimate task fully achieved. 1 out of 1 form submitted.', 'next_step': 'Complete the task and provide final summary of successful form submission.'}]}}]}, 'usage': {'prompt_tokens': 405, 'completion_tokens': 1841, 'total_tokens': 2246, 'prompt_token_details': {'cached_tokens': 0}}}
Step step_Zjli55GkkIRVliNSqS8E5gAb status: completed
  Tool calls:
    Tool Call ID: call_oQLq7fMI7
```

# まとめ
最近は、GitHub CopilotやClaude Codeで、アプリケーションのAPIが工数少なく開発できるため、API（MCP）をLLMがTool呼び出しすることで解決するシーンが多いですが、
サービスによってはAPIが提供されていないこともあります。そういう場合の自動化エージェントとして使ってみるのが良いかもしれません。

複雑なブラウザ操作を、人間がチャットしながら実施することはできますが、チャットする手間が残るなら、人間がブラウザ操作するのでは？とも思うので、
シンプルなシーンの自動化　が一番向いているのかもしれません。
もしくは、Playwright Automationのエージェントを監視するエージェントを用意して、AI同士で連携して、複雑なブラウザ操作を自動化するのも面白いかもしれません。そうなると、gpt-5のような賢さ（Reasoning能力）が必要になるかもしれませんね。