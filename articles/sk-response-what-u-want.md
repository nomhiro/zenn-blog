---
title: "SematicKernelでチャットに対して追加質問する"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["SemanticKernel",".Net","CShar","OpenAI"]
published: false
---

# はじめに


# 検証環境
- DockerDesktop上のコンテナ
- dotnet 7.0.405

# 検証

### コンソールアプリを作成

```
dotnet new console -o SKConsoleApp -f net7.0
```
![](/images/sk-response-what-u-want/2024-01-20-23-36-55.png)

パッケージの取得
```
dotnet add package Microsoft.SemanticKernel --version 1.1.0
```