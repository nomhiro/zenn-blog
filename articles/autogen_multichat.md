---
title: "AutoGenのグループチャットのふるまいを整理する"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: [”autogen”, ”chat”, "OpenAI", "Azure"]
published: false
---

# はじめに
以前のこちらの記事で、AutoGenの概要について解説しました。
https://zenn.dev/nomhiro/articles/autogen-abstract

今回は、複数人による会話のためのグループチャットのふるまいについて整理します。

# グループチャットのふるまい概要
グループチャットは、以下の一連の流れで会話が行われます。
1. 会話するエージェントを選ぶ
2. 選ばれたエージェントが発言する
3. 発言した内容をほかのエージェント全員に配信する
![](/images/autogen_multichat/2024-05-03-15-34-35.png)