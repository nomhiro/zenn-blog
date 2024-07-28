---
title: "SemanticKernelを使ったマルチエージェントをPoCする（QuestionnaireMultiagent）"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Azure", "MultiAgent", "SemanticKernel", "OpenAI"]
published: false
---

# はじめに
2024年 7月25日(木) に東京で開催された Azure OpenAI Service Dev Day にて、MicrosoftのMarcoさんがマルチエージェントについて説明され、SemanticKernelを使ってマルチエージェントを実装したGitHubリポジトリが公開されました。
Vice Presidentの方がご自身で実装され、ご自身でデモをされる姿が非常に印象的でした。
https://aoai-devday.com/session/Multi-model,%20multimodal,%20and%20multi-agent%20innovations%20in%20Azure%20AI
https://github.com/mcasalaina/QuestionnaireMultiagent

このリポジトリのマルチエージェントをPoCしてみます。

# 動かしてみる

### エージェントは以下の４つ
- **QuestionAnswererAgent**
  - 質問に対する回答を生成するエージェント
- **AnswerCheckerAgent**
  - 回答が正しいかを判断するエージェント
- **LinkCheckerAgent**
  - 回答内のリンクが正しいかをチェックするエージェント
- **ManagerAgent**
  - 回答を承認するか判断するエージェント

## 前提
- .NET Core 8.0をインストールしておきます。
https://dotnet.microsoft.com/en-us/download/dotnet/8.0

- VSCodeで実行するための、「ms-dotnettools.csharp」Extensionをインストールしておきます。

## 環境変数の設定
以下の4つを設定します。
- AZURE_OPENAI_API_KEY
  - Azure OpenAIのAPIキー
- AZURE_OPENAI_MODEL_DEPLOYMENT
  - Azure OpenAIのモデルデプロイメント名
- AZURE_OPENAI_ENDPOINT
  - Azure OpenAIのエンドポイントURL
- BING_API_KEY - a key to a Bing Search v7 resource 
  - Bing SearchのAPIキー

Azure OpenAIのモデルはGPT4oを使います。
```json
{
  "AZURE_OPENAI_MODEL_DEPLOYMENT": "gpt-4o",
  "AZURE_OPENAI_ENDPOINT": "https://{AzureOpenAIのリソース名}.openai.azure.com",
  "AZURE_OPENAI_API_KEY": "Azure OpenAIのAPIキー",
  "BING_API_KEY": "Bing SearchのAPIキー"
}
```

:::details Bing SearchのAPIキーの取得方法
https://learn.microsoft.com/ja-jp/bing/search-apis/bing-web-search/create-bing-search-service-resource
Azure PortalでBing Searchのリソースを作成します。
![](/images/semantickernel_multiagent_questionnaire_vol1/2024-07-28-22-08-06.png)

![](/images/semantickernel_multiagent_questionnaire_vol1/2024-07-28-22-14-58.png)
:::

## デバッグ実行


### F5で実行してみましょう。

![](/images/semantickernel_multiagent_questionnaire_vol1/2024-07-28-22-51-44.png)
上記のように画面が表示されます。各入力欄は以下のような目的で使われます。
- Context：**何についての会話か**
- Question：**エージェントに質問する内容**


##### まずは、デフォルトで設定されている質問そのままで試してみます。
```text
Does your service offer video generative AI?
```

Agentからの回答はこちらです。
![](/images/semantickernel_multiagent_questionnaire_vol1/2024-07-28-23-18-57.png)
:::details 回答のテキスト
```text
Question: Does your service offer video generative AI?
QuestionAnswererAgent: Microsoft Azure AI does not currently offer a specific service solely dedicated to video generative AI. However, Azure provides various AI tools and services that can be used in conjunction with other generative AI techniques to handle video content. For example, Azure Video Indexer can connect with other AI models offered by Azure OpenAI to enhance video-related tasks.

For more information on Azure Video Indexer and its capabilities, refer to the [Microsoft Azure documentation](https://learn.microsoft.com/en-us/azure/azure-video-indexer/).
AnswerCheckerAgent: ANSWER INCORRECT - Azure does not currently offer a specific service solely dedicated to video generative AI.
LinkCheckerAgent: LINK INCORRECT - https://learn.microsoft.com/en-us/azure/azure-video-indexer/
ManagerAgent: reject
QuestionAnswererAgent: Microsoft Azure AI does not offer a specific service solely dedicated to video generative AI. However, Azure provides various AI tools and services such as Azure Video Indexer which can connect to other AI models from Azure OpenAI, allowing for some advanced video content manipulation capabilities in combination with other generative AI techniques. 

For further details on the capabilities of Azure Video Indexer, please refer to [Microsoft Azure Video Indexer documentation](https://learn.microsoft.com/en-us/azure/azure-video-indexer/).
AnswerCheckerAgent: ANSWER CORRECT.
LinkCheckerAgent: LINKS CORRECT
ManagerAgent: approve
```
:::

- 1回目の会話
  - 「AnswerCheckerAgent」：**回答が間違っていると判断**
  - 「LinkCheckerAgent」：**リンクが間違っていると判断**
  - 「ManagerAgent」：**回答を拒否**
- 2回目の会話
  - 「AnswerCheckerAgent」：**回答が正しいと判断**
  - 「LinkCheckerAgent」：**リンクが正しいと判断**
  - 「ManagerAgent」：**回答を承認**


##### 次には、日本語で以下のような質問をしてみます。
```text
Azure でLlamaを使える？
```

![](/images/semantickernel_multiagent_questionnaire_vol1/2024-07-28-23-43-07.png)

良さそうですね。リンクの修正が実施されました。

:::details 回答のテキスト
```text
Question: Azure でLlamaを使える？
QuestionAnswererAgent: はい、Microsoft AzureではMeta Llama 3モデルを利用できます。Azure AIモデルカタログには、Meta-Llama-3-8B-InstructやMeta-Llama-3-70B-Instructなどのモデルが含まれており、これらは事前トレーニングおよびインストラクションに基づいたファインチューニングモデルです。これらのモデルはAzure AI Studioで利用可能で、サーバーレスAPIやその他のデプロイメントオプションを使用して展開できます。

例えば、「Meta-Llama-3.1-405B-Instruct」モデルをサーバーレスAPIとしてデプロイすることができますが、この機能を利用するにはワークスペースがEast US 2またはSweden Centralリージョンに属している必要があります。

詳細はこちらを参照してください：
- [Azure AIとMeta Llamaの統合](https://learn.microsoft.com/azure/ai-services/?pivots=api)
AnswerCheckerAgent: ANSWER CORRECT
LinkCheckerAgent: LINK INCORRECT - https://learn.microsoft.com/azure/ai-services/?pivots=api
ManagerAgent: reject
QuestionAnswererAgent: はい、Microsoft AzureではMeta Llama 3モデルを利用できます。Azure AIモデルカタログには、Meta-Llama-3-8B-InstructやMeta-Llama-3-70B-Instructなどのモデルが含まれており、これらは事前トレーニングおよびインストラクションに基づいたファインチューニングモデルです。これらのモデルはAzure AI Studioで利用可能で、サーバーレスAPIやその他のデプロイメントオプションを使用して展開できます。

たとえば、「Meta-Llama-3.1-405B-Instruct」モデルをサーバーレスAPIとしてデプロイすることができますが、この機能を利用するにはワークスペースがEast US 2またはSweden Centralリージョンに属している必要があります。

詳細情報はこちらを参照してください：
- [Meta Llama on Azure](https://techcommunity.microsoft.com/t5/ai-applied-ai-blog/introducing-meta-llama-3-models-on-azure-open-datasets/ba-p/3937513)
AnswerCheckerAgent: はい、Microsoft AzureではMeta Llama 3モデルを利用できます。Azure AIモデルカタログには、Meta-Llama-3-8B-InstructやMeta-Llama-3-70B-Instructなどのモデルが含まれており、これらは事前トレーニングおよびインストラクションに基づいたファインチューニングモデルです。これらのモデルはAzure AI Studioで利用可能で、サーバーレスAPIやその他のデプロイメントオプションを使用して展開できます。

たとえば、「Meta-Llama-3.1-405B-Instruct」モデルをサーバーレスAPIとしてデプロイすることができますが、この機能を利用するにはワークスペースがEast US 2またはSweden Centralリージョンに属している必要があります。

詳細情報はこちらを参照してください：
- [Meta Llama on Azure](https://techcommunity.microsoft.com/t5/ai-applied-ai-blog/introducing-meta-llama-3-models-on-azure-open-datasets/ba-p/3937513)
LinkCheckerAgent: LINKS CORRECT
ManagerAgent: approve
```
:::

- 1回目の会話
  - 「AnswerCheckerAgent」：**回答が正しいと判断**
  - 「LinkCheckerAgent」：**リンクが間違っていると判断**
  - 「ManagerAgent」：**回答を拒否**
- 2回目の会話
  - 「AnswerCheckerAgent」：**回答が正しいと判断**
  - 「LinkCheckerAgent」：**リンクが正しいと判断**
  - 「ManagerAgent」：**回答を承認**


# 内部実装の解説

## エージェントの呼び出し方

各エージェントの処理は、QuestionAnswererAgent、AnswerCheckerAgent、LinkCheckerAgent、ManagerAgentの順で呼び出されます。
```csharp
AgentGroupChat chat =
  new(QuestionAnswererAgent, AnswerCheckerAgent, LinkCheckerAgent, ManagerAgent)
  {
    ExecutionSettings =
      new()
      {
        TerminationStrategy =
          new ApprovalTerminationStrategy()
          {
            Agents = [ManagerAgent],
            MaximumIterations = 25,
          }
      }
  };

string input = Question;

chat.AddChatMessage(new ChatMessageContent(AuthorRole.User, input));

updateResponseBox("Question", input);

await foreach (var content in chat.InvokeAsync())
{
  // 画面表示の色設定（省略）

  updateResponseBox(content.AuthorName,content.Content,color);
}
```

## 会話を終了する条件
ManagerAgentが承認するか、指定された回数だけ会話が行われると、会話が終了します。
```csharp
namespace QuestionnaireMultiagent
{
  class ApprovalTerminationStrategy : TerminationStrategy
  {
    // Terminate when the final message contains the term "approve"
    protected override Task<bool> ShouldAgentTerminateAsync(Agent agent, IReadOnlyList<ChatMessageContent> history, CancellationToken cancellationToken)
        => Task.FromResult(history[history.Count - 1].Content?.Contains("approve", StringComparison.OrdinalIgnoreCase) ?? false);
  }
}
```

## 内部で使われているプロンプト

- **QuestionAnswererAgent**
```text
You are a question answerer for {Context}.
You take in questions from a questionnaire and emit the answers from the perspective of {Context},
using documentation from the public web. You also emit links to any websites you find that help answer the questions.
Do not address the user as 'you' - make all responses solely in the third person.
```
Contextは、画面から入力される質問のトピックです。何に関する質問なのかを指定します。

- **AnswerCheckerAgent**
```text
You are an answer checker for {Context}. Your responses always start with either the words ANSWER CORRECT or ANSWER INCORRECT.
Given a question and an answer, you check the answer for accuracy regarding {Context},
using public web sources when necessary. If everything in the answer is true, you verify the answer by responding "ANSWER CORRECT." with no further explanation.
Otherwise, you respond "ANSWER INCORRECT - " and add the portion that is incorrect.
You do not output anything other than "ANSWER CORRECT" or "ANSWER INCORRECT - <portion>".
```
質問と回答を受け取り、回答が正しいかを判断します。
間違っている場合は、間違っている部分を指摘します。

- **LinkCheckerAgent**
```text
You are a link checker. Your responses always start with either the words LINKS CORRECT or LINK INCORRECT.
Given a question and an answer that contains links, you verify that the links are working,
using public web sources when necessary. If all links are working, you verify the answer by responding "LINKS CORRECT" with no further explanation.
Otherwise, for each bad link, you respond "LINK INCORRECT - " and add the link that is incorrect.
You do not output anything other than "LINKS CORRECT" or "LINK INCORRECT - <link>".
```
回答内のリンクが機能するかをチェックします。
間違っている場合は、間違っているリンクを指摘します。

- **ManagerAgent**
```text
You are a manager which reviews the question, the answer to the question, and the links.
If the answer checker replies "ANSWER INCORRECT", or the link checker replies "LINK INCORRECT," you can reply "reject" and ask the question answerer to correct the answer.
Once the question has been answered properly, you can approve the request by just responding "approve".
You do not output anything other than "reject" or "approve".
```
質問、質問への回答、リンクを確認し、回答が正しいかを判断します。

## Bing SearchのAPIの扱い
BingSearchのAPい呼び出しは、SemanticKernelのプラグインとしてインポートされています。
各エージェントのシステムプロンプトにより、SemanticKernelがBindSearchのAPIを呼び出し有無を判断します。
```csharp
BingConnector bing = new BingConnector(BING_API_KEY);

kernel.ImportPluginFromObject(new WebSearchEnginePlugin(bing), "bing");
```

# まとめ
このように、公開されたGitHubリポジトリを参照し、SemanticKernelを使ってマルチエージェントをPoCすることができました。
このように、成果物に対してレビューし、承認するプロセスを自動化することがマルチエージェントの活用方法の一つですね。
今回の実装では、エージェントを順番に呼び出していますが、会話の内容によって呼び出すエージェントを動的にすることで、より複雑な会話を複数のエージェントで解決することができるかもしれません。

今回の実装はC#ですが、Pythonで同じことができるか、見てみようと思います。（SemanticKernel側のサポート次第ですね）
