---
title: "API Management による Agentic World"
emoji: "📌"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

オーケストレーションする側と、専門家AIエージェントを提供する側の関係を考えると、API Management が重要な役割を果たす。

AIエージェントがマイクロサービスとしてAPI公開されている。

オーケストレーションが複数の専門家AIのAPIを使い、AIエージェントを組み合わせた仕組みにする場合
- 専門家APIごとに異なるAPI仕様の吸収（APIごとにオーケストレーション側に実装を組み込むのはナンセンス）。最低限のルールは必要
- 