---
title: "AzureOpenAI GPT4Visionを使ってExcelをデータ化する"
emoji: "🦔"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# はじめに



# 検証環境


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