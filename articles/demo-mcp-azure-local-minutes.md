---
title: ""
emoji: "🙌"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# Filesystem MCP

VSCodeの拡張機能を使って、ローカルのファイルシステムをMCPとして扱うことができるようにする。

Ctrl+Shift+Pでコマンドパレットを開き、「MCP: Add Server」を選択する。
![](/images/demo-mcp-azure-local-minutes/2025-05-22-19-05-38.png)

```
@modelcontextprotocol/server-filesystem
```
![](/images/demo-mcp-azure-local-minutes/2025-05-22-19-05-29.png)

![](/images/demo-mcp-azure-local-minutes/2025-05-22-19-06-21.png)

![](/images/demo-mcp-azure-local-minutes/2025-05-22-19-07-03.png)

![](/images/demo-mcp-azure-local-minutes/2025-05-22-19-07-42.png)

Workspace SettingとしてMCP Serverを追加する。
![](/images/demo-mcp-azure-local-minutes/2025-05-22-19-14-29.png)

.vscode フォルダに mcp.json が作成されます。
```json
{
  "servers": {
    "filesystem-minutes": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${input:baseDirectory}",
        "PLACEHOLDER_FOR_ALLOWED_DIRECTORY"
      ]
    }
  },
  "inputs": [
    {
      "id": "baseDirectory",
      "type": "promptString",
      "description": "Enter the base directory path for the server"
    }
  ]
}
```