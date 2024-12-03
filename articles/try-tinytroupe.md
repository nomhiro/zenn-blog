---
title: "マルチエージェントペルソナシミュレーション TinyTroupe とは？？？ "
emoji: "💁"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["マルチエージェント", "LLM", "TinyTroupe", "GPT4o"]
published: false
---

# はじめに
LLMが登場してから、役割や実行することが異なる複数のAIエージェントを組み合わせる、マルチエージェントシステムが注目されています。Microsoft Ignite 2024でも、マルチエージェントに関わるセッションが多く開催されました。

こちらの記事にて、Igniteでトヨタ自動車のマルチエージェントシステム"O-beya"が発表されており、詳細が詳しくまとめられています。
担当して構築した仕組みがこのように公表されたことが非常に嬉しく思います...!!!
https://qiita.com/nohanaga/items/093488c3a69c3c2d55ba

さて、この記事の本題はここからです。
マルチエージェントシステムについて、たまたまMicrosoftのGitHubのリポジトリに面白そうなマルチエージェントペルソナシミュレーションがありましたので、技術観点の興味でお試ししてみます。

※GitHubリポジトリより引用 <https://github.com/microsoft/TinyTroupe>
![](/images/try-tinytroupe/2024-11-24-19-12-38.png)


# TinyTroupeとは？？？
GitHubのREADMEには以下のように記載されています。
**想像力の向上とビジネスインサイトのためのLLMを活用したマルチエージェントペルソナシミュレーション**

