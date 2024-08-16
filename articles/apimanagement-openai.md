---
title: "Azure API Managementを使たOpenAIの負荷分散"
emoji: "🎉"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

https://learn.microsoft.com/ja-jp/azure/developer/python/get-started-app-chat-scaling-with-azure-api-management?tabs=github-codespaces%2Cinitial-deployment

https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/intelligent-load-balancing-with-apim-for-openai-weight-based/ba-p/4115155

# OpenAIのTPUについて


# Azure API Managementの負荷分散について

OpenAIのTPM上限になると、HTTP429エラーが返されます。ALMManagementでは、一つのエンドポイント（OpenAI）で429エラーになった場合、そのエンドポイントが再度リクエストを受け付けるまで、別のエンドポイントにリクエストを送信するポリシーを定義できます。

### 負荷分散のポリシー

APIManagementの負荷分散は以下3つのポリシーが定義できます。TPMを考慮して負荷分散するためには、**Priority**を使います。
- **Priority**
  - 一つのエンドポイントが429エラーになった場合、優先度に基づいて利用可能なOpenAIエンドポイントにリクエストを送信します。
- **RoundRobin**
  - TPMは考慮せず、トラフィックを**順番に**分散する方法です。TPMに達した場合、429エラーが返されます。
- **Random**
  - RoundRobinとほぼ同じで、TPMは考慮せずにトラフィックを**ランダム**に選択します。

## Priorityポリシーの概要

Priorityポリシーを定義するには、自前でPolicy定義を書く必要があります。

### バックエンドが選ばれる処理概要

Priorityと聞くと、必ず優先順に選ばれるイメージを持ちますが、そうではありません。**優先度を高く設定したバックエンドが選ばれる確率が高くなる**という仕組みです。
OpenAIリソースが3つある場合を例に説明します。
| エンドポイント | リソース | リージョン | 重み |
| --- | --- | --- | --- |
| エンドポイント1 | OpenAI GPT4o | East US | 600 |
| エンドポイント2 | OpenAI GPT4o | North Central US | 300 |
| エンドポイント3 | OpenAI GPT4o | South Central US | 50 |

1. まず、各リソースの重みの総重量が計算されます。
   - 600 + 300 + 50 = 950
2. 累積重量が計算され、各エンドポイントに対応する範囲が計算されます。
  - エンドポイント1(EastUS)：1 ~ 600
  - エンドポイント2(NorthCentralUS)：600 ~ 900（600+300）
  - エンドポイント3(SouthCentralUS)：900 ~ 950（600+300+50）
3. 1から総重量までの間でランダムな数値を生成します。ここでは1から950の間です。
4. ランダムな数値が、どの2.の範囲に含まれるか判定し、そのエンドポイントにリクエストを送信します。

![](/images/apimanagement-openai/2024-06-16-10-31-25.png)

確率的には、
- エンドポイント1(EastUS)：63.2% (600/950)
- エンドポイント2(NorthCentralUS)：31.6% (300/950)
- エンドポイント3(SouthCentralUS)：5.3% (50/950)

### TPM制限になった場合のふるまい

エンドポイント1がTPM制限になった場合。
![](/images/apimanagement-openai/2024-06-16-10-36-30.png)

- エンドポイント1はHTTP429エラーになります。
- 残りのエンドポイント2と3を使い、重みが大きいエンドポイント2が選ばれる確率が高くなります。
- TPM制限になったエンドポイント1は、正常性プルーブ要求が再試行される


# 設定

## OpenAIのリソースを3つ作成
- aoai-eastus-apimtest-001
- aoai-ncu-apimtest-001
- aoai-scu-apimtest-001

![](/images/apimanagement-openai/2024-06-15-16-57-21.png)

すべてのOpenAIリソースにGPT4oをデプロイします。
:::message
APIManagementで負荷分散を行うため、デプロイ名は同じにする必要があります。
:::

## APIManagementの作成

![](/images/apimanagement-openai/2024-06-15-13-19-19.png)

![](/images/apimanagement-openai/2024-06-15-13-14-00.png)

プライベートネットワーク内のVMから接続するため、プライベートエンドポイントを作成します。
![](/images/apimanagement-openai/2024-06-15-13-15-38.png)

![](/images/apimanagement-openai/2024-06-15-13-16-01.png)

そのほかはデフォルト設定です。

![](/images/apimanagement-openai/2024-06-15-13-19-47.png)

## ApplicationInsightsの作成

APIManagementのモニタリングのためにApplicationInsightsを作成します。

![](/images/apimanagement-openai/2024-06-15-14-34-49.png)

![](/images/apimanagement-openai/2024-06-15-14-35-02.png)


## APIManagementのマネージドIDにOpenAIのロール付与

APIManagementのマネージドIDを有効にします。
![](/images/apimanagement-openai/2024-06-15-17-16-33.png)

OpenAIのリソースにAPIManagementのマネージドIDをRBAC「Cognitive Services OpenAI User」で追加します。
※すべてのOpenAIリソースに設定します。

![](/images/apimanagement-openai/2024-06-15-17-21-57.png)

![](/images/apimanagement-openai/2024-06-15-17-18-40.png)

## API（OpenAI）の設定

二つのポリシーが設定できます。
※後から設定変更するので、設定なしでもOKです。
- Manage token consumption
  - OpenAIのトークンに制限を設け、過剰使用を防ぐ設定
- Track token usage
  - 消費した合計トークン数を補完するための設定
  Metric dimensionsは、選択したdimensionでグループ化するための設定

![](/images/apimanagement-openai/2024-06-15-14-54-41.png)

![](/images/apimanagement-openai/2024-06-15-14-54-51.png)

## 追加Inbound processing

![](/images/apimanagement-openai/2024-06-15-17-34-02.png)

以下のXMLに変更
```xml
<policies>
    <inbound>
        <base />
        <authentication-managed-identity resource="https://cognitiveservices.azure.com" />
        <set-variable name="urlId" value="@(new Random(context.RequestId.GetHashCode()).Next(1, 3))" />
        <choose>
            <when condition="@(context.Variables.GetValueOrDefault<int>("urlId") == 1)">
                <set-backend-service base-url="{{backend-url-1}}" />
            </when>
            <when condition="@(context.Variables.GetValueOrDefault<int>("urlId") == 2)">
                <set-backend-service base-url="{{backend-url-2}}" />
            </when>
            <otherwise>
                <!-- Should never happen, but you never know ;) -->
                <return-response>
                    <set-status code="500" reason="InternalServerError" />
                    <set-header name="Microsoft-Azure-Api-Management-Correlation-Id" exists-action="override">
                        <value>@{return Guid.NewGuid().ToString();}</value>
                    </set-header>
                    <set-body>A gateway-related error occurred while processing the request.</set-body>
                </return-response>
            </otherwise>
        </choose>
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
```

```xml
<policies>
    <inbound>
        <set-backend-service id="apim-generated-policy" backend-id="aoai-eastus-apitest-001-openai-endpoint" />
        <azure-openai-token-limit tokens-per-minute="1000" counter-key="@(context.Subscription.Id)" estimate-prompt-tokens="true" tokens-consumed-header-name="consumed-tokens" remaining-tokens-header-name="remaining-tokens" />
        <azure-openai-emit-token-metric>
            <dimension name="API ID" />
        </azure-openai-emit-token-metric>
        <authentication-managed-identity resource="https://cognitiveservices.azure.com/" />
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>