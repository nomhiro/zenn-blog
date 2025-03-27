---
title: ""
emoji: "🐡"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# PoC

## MCPを実行するクライアントアプリの実装

Next.jsのアプリケーションを作成し、MCPを実行するクライアントアプリを作成します。
```bash
npx create-next-app@latest mcp-app-browser-test
```

MCPクライアントを実装するためのパッケージ "ai-context-protocol" をインストールします。
```bash
npm install model-context-protocol @ai-sdk/react
```

こっちを試したほうがよさそう
https://vercel.com/blog/ai-sdk-4-2#model-context-protocol-(mcp)-clients
https://sdk.vercel.ai/docs/ai-sdk-core/tools-and-tool-calling#using-mcp-tools


これはそのあと　Playwrite
https://vercel.com/blog/ai-sdk-4-2#model-context-protocol-(mcp)-clients

あとこれもそのあと　AIAgentMCP
