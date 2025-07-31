---
title: "【SLM×MCP】SLM（phi-4-mini）からMCPを使ってツールを呼び出したい"
emoji: "🧰"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["mcp", "slm", "aifoundry", "phi"]
published: false
---

# はじめに
本記事では、ローカルで動作する小規模言語モデル（SLM）とModel Context Protocol（MCP）を連携するコードを解説します。

https://github.com/nomhiro/slm-mcp

# SLM（Small Language Model）とは
SLMは、GPT-4.1などの大規模モデルと比べてパラメータ数が少ない言語モデルです。例えばMicrosoft Phi-4（14B）などがあります。

- ローカルで実行できる（レスポンスは遅いが、CPUでも動作）
- ネットワーク遅延はなくなる
- データが外部に送信されない
- API使用料がかからない

詳細はこちらにて！
https://zenn.dev/nomhiro/articles/slm-foundry-local-poc-01#slm%EF%BC%88small-language-model%EF%BC%89%E3%81%A8%E3%81%AF%EF%BC%9F

# MCP（Model Context Protocol）とは
MCPはAnthropic社が開発したプロトコルで、AIモデルが外部ツールやリソースを安全に使えるようにする標準仕様です。

詳細はこちらにて！
https://zenn.dev/nomhiro/articles/neo4j-mcp-person-knowledge#%EF%BC%88%E3%81%8A%E3%81%95%E3%82%89%E3%81%84%EF%BC%89mcp%E3%81%A8%E3%81%AF%EF%BC%9F

# 試した内容

こちらのGitHubにSLM×MCP連携のツールを公開しています。

こんな感じで動作します。
指示に従いMCPのツールを介してローカルファイルの内容を読み、指示に応答します。ローカル環境のSLMを使っているのでオフラインでも動作します。
```powershell
💬 あなた: C:\Users\nom40\Documents\PoC\20_slm\slm-mcp\README.md　の内容を100字で要約して教えて

🔄 考えています...

🤖 アシスタント: 2025-07-31 22:11:42,276 - httpx - INFO - HTTP Request: POST http://localhost:5273/v1/chat/completions "HTTP/1.1 200 OK"
申し訳ありませんが、ファイルシステムにアクセスすることはできません。ただし、ファイルの内容を読み取るための指示を提供できます:

[{"name": "read_file", "parameters": {"path": "C:\\Users\\nom40\\Documents\\PoC\\20_slm\\slm-mcp\\README.md"}}]


ファイルの内容を100字で要約するには、ファイルを読み取った後、要約を作成する必要があります。これはAIとして、ファイルシステムに直接アクセスすることはできません。要約を作成するための手順は、上記のJSONオブジ ェクトを使用してファイルの内容を取得することです。

🔧 Phi ツール実行確認
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ツール: read_file
説明: Read the complete contents of a file from the file system. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Use the 'head' parameter to read only the first N lines of a file, or the 'tail' parameter to read only the last N lines of a file. Only works within allowed directories.       
パラメータ:
{
  "path": "C:\\Users\\nom40\\Documents\\PoC\\20_slm\\slm-mcp\\README.md"
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


選択してください:
  [Y] はい - ツールを実行
  [N] いいえ - 実行をキャンセル
  [S] 詳細 - 実行パラメータを確認

入力 (Y/N/S): Y
2025-07-31 22:12:04,674 - slm_mcp.core.mcp_manager - INFO - Tool 'read_file' executed successfully in 2.74s
✅ ツール実行成功: read_file

🤖 アシスタント: 2025-07-31 22:13:08,818 - httpx - INFO - HTTP Request: POST http://localhost:5273/v1/chat/completions "HTTP/1.1 200 OK"
提供された `read_file` ツールの実行結果に基づいて、ファイル `README.md` の要約は次の通りです:

ローカル小規模言語モデル（SLM）とModel Context Protocol（MCP）の統合パッケージ
SLM-MCPは、ローカルで動作するPhiシリーズ（Phi-4、Phi-4-mini等）の小規模言語モデルと、MCPサーバーを連携させて、ファイルシステム操作などの豊富な機能を提供するPythonパッケージです。
```

# 先に結論

phi-4-mini は、システムメッセージ等の指示の効きにくさと、gpt-3.5時代を思い出す推論能力だな という感触です。
利用シーンはオフライン環境などと限定的です。が、、試してみましたのでどこかで参考になればと思います。

# ツールの解説

### 統合アーキテクチャの設計思想

MCP以前はモデルとツールが密接に結びついていましたが、ツールとAIモデルを以下のようにします。

- MCPによりツール一覧とツール説明の情報を交換
- SLMが自然言語でツール呼び出し意図を抽出
- 自然言語の意図を構造化されたAPIコールに変換
- 実際のツール実行とリソースアクセス
- ツール実行結果を自然言語で解釈して提示

# ツール起動方法

## 環境構築

まず、必要な依存関係をインストールします。
ここでは、例としてfilesystemMCPを利用します。

```bash
# Python環境の準備
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install openai mcp pydantic httpx

# MCP Filesystem Serverのインストール
npm install -g @modelcontextprotocol/server-filesystem
```

## SLMのセットアップ

phi-4-miniを使います。FoundryLocalを使用してPhi-4-miniを起動します。
SLMが問題なく動作しているか、確認しましょう。

▼ Phi-4-miniモデルをダウンロードして実行まで行う場合
```bash
foundry model run phi-4-mini
```

▼ phi-4-mini モデルのダウンロード、サービス開始を分けて実行する場合
```bash
# 1. モデルをダウンロード
foundry model download phi-4-mini

# 2. サービスを開始（必要に応じて）
foundry service start

# 3. モデルをロード
foundry model load phi-4-mini
```

## MCPサーバーの設定

設定ファイル（`config.json`）を作成します。
`/path/to/allowed/directory` はお使いの環境に合わせて、filesystemMCPに操作を許可するフォルダパスを指定してください。

```json
{
  "slm": {
    "alias": "phi-4-mini",
    "base_url": "http://localhost:8080/v1",
    "api_key": "local"
  },
  "mcp_servers": [
    {
      "name": "filesystem",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/directory"
      ],
      "allowed_paths": [
        "/path/to/allowed/directory"
      ]
    }
  ],
  "settings": {
    "system_message": "あなたは親切なAIアシスタントです。ファイルシステムにアクセスして、ユーザーの要求に応えることができます。"
  }
}
```

## 起動

`--config`で一つ前の手順で定義したconfigのJsonファイルを指定して実行してください。
※指定していない場合はdefault_config.jsonが使われます。
```
python .\run_slm_mcp.py --config test_config.json
```

以下のように表示されていれば問題なく起動できています。
```powershell
(.venv) 20_slm\slm-mcp > python .\run_slm_mcp.py --config test_config.json
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
2025-07-31 22:31:16,652 - slm_mcp.cli.main - INFO - Initializing SLM client with alias: phi-4-mini
2025-07-31 22:31:18,882 - httpx - INFO - HTTP Request: GET http://localhost:5273/foundry/list "HTTP/1.1 200 OK"
2025-07-31 22:31:19,166 - httpx - INFO - HTTP Request: GET http://localhost:5273/openai/models "HTTP/1.1 200 OK"
2025-07-31 22:31:23,315 - httpx - INFO - HTTP Request: GET http://localhost:5273/openai/load/Phi-4-mini-instruct-generic-cpu?ttl=600 "HTTP/1.1 200 OK"
2025-07-31 22:31:23,606 - slm_mcp.cli.main - INFO - Connecting to 1 MCP servers...
2025-07-31 22:31:26,113 - slm_mcp.core.mcp_manager - INFO - Retrieved 12 tools from filesystem
2025-07-31 22:31:26,153 - slm_mcp.core.mcp_manager - INFO - Connected to MCP server 'filesystem' with 12 tools
2025-07-31 22:31:26,153 - slm_mcp.core.mcp_manager - INFO - Connected to 1/1 MCP servers
2025-07-31 22:31:26,155 - slm_mcp.core.mcp_manager - INFO - Available tools: ['read_file', 'read_multiple_files', 'write_file', 'edit_file', 'create_directory', 'list_directory', 'list_directory_with_sizes', 'directory_tree', 'move_file', 'search_files', 'get_file_info', 'list_allowed_directories']

🤖 SLM MCP統合アシスタント
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 SLMモデル: phi-4-mini
🔗 MCPサーバー: 1 接続
🛠️  利用可能なツール: 12 個


📖 読み取り系:
  • read_file: Read the complete contents of a file from the file...
  • read_multiple_files: Read the contents of multiple files simultaneously...

✏️ 書き込み系:
  • write_file: Create a new file or completely overwrite an exist...
  • edit_file: Make line-based edits to a text file. Each edit re...

📁 ディレクトリ系:
  • create_directory: Create a new directory or ensure a directory exist...
  • list_directory: Get a detailed listing of all files and directorie...
  • list_directory_with_sizes: Get a detailed listing of all files and directorie...
  • ... 他 2 個

🔧 その他:
  • move_file: Move or rename files and directories. Can move fil...
  • search_files: Recursively search for files and directories match...
  • get_file_info: Retrieve detailed metadata about a file or directo...

コマンド:
  • exit       - 終了
  • noconfirm  - ツール実行確認を無効化
  • confirm    - ツール実行確認を有効化
  • tools      - 利用可能なツールを再表示
  • stats      - 実行統計を表示
  • clear      - 会話履歴をクリア
  • config     - 設定を表示
  • addpath    - 許可されたパスを追加
  • listpaths  - 許可されたパスを表示
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


💬 あなた:
```

# 実装解説

## ツール呼び出しの実装

SLMからMCPツールを呼び出すためのオーケストレーターを実装します。


```python
class PhiToolOrchestrator:
    def __init__(self, mcp_manager: MCPClientManager, openai_client, model_id: str,
                 max_tokens: int = 4096, temperature: float = 0.7, 
                 parallel_execution: bool = False):
        self.mcp_manager = mcp_manager
        self.openai_client = openai_client
        self.model_id = model_id
        self.monitor = ToolExecutionMonitor()
        
        # LLM設定
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.parallel_execution = parallel_execution
        
        # 責任を分離したヘルパークラス
        self.conversation_manager = ConversationManager()
        self.tool_parser = PhiToolParser()
    
    async def execute_conversation_turn(self, user_message: str, 
                                      require_confirmation: bool = True) -> str:
        """1回の会話ターンを実行"""
        
        # 1. 利用可能なツールを取得（MCPManagerから既にOpenAI形式で取得）
        available_tools = self.mcp_manager.get_available_tools()
        
        # 2. システムメッセージを更新（ツール情報を含む）
        system_message = self.create_system_message_with_tools(available_tools)
        
        # システムメッセージを更新
        self.conversation_manager.update_system_message(system_message)
        
        # 3. ユーザーメッセージを履歴に追加
        self.conversation_manager.add_user_message(user_message)
        
        # 4. LLMに送信（ストリーミング応答）
        assistant_content = await self._stream_llm_response()
        
        # 5. ツール呼び出しを解析
        tool_calls = self.tool_parser.parse_tool_calls(assistant_content, self.mcp_manager.tools)
        
        # 6. ツールを実行
        if tool_calls:
            await self._execute_tools_parallel_or_sequential(tool_calls, require_confirmation)
            
        return assistant_content
```

### ツール呼び出しパーサーの実装詳細

SLMの出力からツール呼び出しの内容を抽出しています。

```python
class PhiToolParser:
    def __init__(self):
        pass
    
    def parse_tool_calls(self, content: str, available_tools: Dict[str, Any]) -> List[Dict[str, Any]]:
        """SLMの応答からツール呼び出しを抽出"""
        tool_calls = []
        
        # JSON形式のツール呼び出しを抽出
        json_blocks = self._extract_json_blocks(content)
        
        for block in json_blocks:
            try:
                # JSONとして直接パース
                parsed_data = json.loads(block)
                
                # 配列形式の場合
                if isinstance(parsed_data, list):
                    for item in parsed_data:
                        if self._is_valid_tool_call(item, available_tools):
                            tool_calls.append(item)
                # 単一オブジェクト形式の場合
                elif isinstance(parsed_data, dict):
                    if self._is_valid_tool_call(parsed_data, available_tools):
                        tool_calls.append(parsed_data)
                        
            except json.JSONDecodeError:
                # JSONパースに失敗した場合は無視
                continue
                
        return tool_calls
    
    def _extract_json_blocks(self, content: str) -> List[str]:
        """テキストからJSONブロックを抽出"""
        import re
        
        # 配列形式とオブジェクト形式の両方に対応
        patterns = [
            r'\[{.*?}\]',  # 配列形式
            r'{[^{}]*"name"[^{}]*"parameters"[^{}]*}'  # オブジェクト形式
        ]
        
        json_blocks = []
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                json_blocks.append(match.group())
                
        return json_blocks
    
    def _is_valid_tool_call(self, call: Dict[str, Any], available_tools: Dict[str, Any]) -> bool:
        """ツール呼び出しの妥当性を検証"""
        if not isinstance(call, dict):
            return False
            
        tool_name = call.get("name")
        if not tool_name or tool_name not in available_tools:
            return False
            
        # パラメータが辞書形式であることを確認
        parameters = call.get("parameters", {})
        return isinstance(parameters, dict)
```

## ストリーミング対応

SLMからの応答のストリーミングレスポンスを実装します。

```python
async def _stream_llm_response(self, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
    """LLMからストリーミングレスポンスを取得する共通メソッド"""
    try:
        assistant_content = ""
        print("\n🤖 アシスタント: ", end="", flush=True)
        
        response = self.openai_client.chat.completions.create(
            model=self.model_id,
            messages=self.conversation_manager.conversation_history,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature or self.temperature,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
                content_chunk = chunk.choices[0].delta.content
                assistant_content += content_chunk
                print(content_chunk, end="", flush=True)
        
        print()
        return assistant_content
    except Exception as e:
        print()  # エラー時も改行
        raise e
```

