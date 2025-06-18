---
title: "Neo4jのMCPを使って、グラフデータベースに自然言語で問い合わせよう！！！"
emoji: "🧠"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Neo4j", "MCP", "Graph Database", "AI"]
published: true
---

![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-36-04.png)

# はじめに

Neo4jとは、グラフデータベースの一種で、ノードとリレーションシップを使ってデータを表現します。
グラフデータベースのクエリを知らない人でも、自然言語で簡単に問い合わせて結果を得られるといいなーと思い、Neo4jのMCP（Model Context Protocol）を使ってみました。

# （おさらい）MCPとは？
知ってるよ！という方は読み飛ばしてください。

MCPとは、アプリケーションがLLMにコンテキストを提供する方法を標準化するオープンプロトコルです。つまり、LLMが他のツールを呼び出しデータ取得やツール実行を行うためのプロトコルです。

ここまで聞くと、従来のFunctionCallingと何が異なる？となりますよね。
FunctionCallingの場合、LLMアプリケーションの中でFunctionのスキーマを定義する必要がありました。また、FunctionCallingで選ばれたツールの実行はコーディングする必要がありました。

MCPの場合は、以下の図のとおり、ツールは別のサーバやプロセスにて独立して動作できます。MCPは、MCPクライアントとMCPサーバで分かれています。LLMアプリケーションとは独立し、MCPクライアントに実装できるのでLLMアプリと分離して管理可能です。

![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-28-45.png)

# Neo4jとMCP

Neo4jのMCPは、以下のような機能を提供しています。

* **MCP-Neo4j-Cypher**: AIが自然言語で指示を出すと、Neo4jデータベースからデータを検索したり更新したりするための**Cypherクエリ**（Neo4j独自の問い合わせ言語）を自動的に生成して実行できます。例えば、「あの顧客の最近の購入履歴を見せて」と問い合わせるだけで、自動でデータベースに問い合わせて情報を引き出してくれます。
* **MCP-Neo4j-Memory**: AIとの長い会話や複雑な計画から得られた情報を、Neo4jにナレッジグラフとして保存・管理できます。これにより、AIは過去の情報を忘れることなく、より一貫した対話や複雑なタスクの実行が可能になります。
* **MCP-Neo4j-Aura-Manager**: 開発者がAIチャットから直接、Neo4j Auraクラウドサービスのデータベースインスタンスを管理できるようになります。データベースの作成、削除、停止、再開などが簡単に行えるようになり、開発効率が向上します。

https://neo4j.com/developer/genai-ecosystem/model-context-protocol-mcp/

このブログでは、**MCP-Neo4j-Cypher**の機能を使ってみます。

# ユースケース
会社に所属する人の得意領域がグラフデータベースに登録されていることを想定します。
例えば、佐藤花子さんは「文書デジタル化:5」「データベース設計:5」「クラウド運用:4」などの得意領域を持っているとします。5が最も得意であることを示します。

以下のようなグラフです。
※データはサンプルであり、AIが生成した架空の人物名です。
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-01-29.png)

グラフデータで持つ意味は、relationに重みを付けられることです。
誰がどの分野に**どのくらい詳しいか**を表現できます。
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-02-30.png)


このようなグラフデータベースに対して、気軽に自然言語で問い合わせて、
「**～～について詳しい人って誰？**　」
と聞いて教えてほしい！
というケースを想定してみましょう。

以下の流れで進めます。
PoCなのでNeo4jはローカルのDockerコンテナで立てます。

1. Neo4jに登録するデータを準備します
2. docker-composeでNeo4jを立てます
3. Neo4jにデータを登録します
4. Neo4jのMCPを使って、自然言語で問い合わせます。（VSCodeのGitHubCopilot Chatを使います。）

# PoC🚀

## 1. Neo4jに登録するデータを準備します
importフォルダに4つのcypherクエリを用意します。
1. persons.cypher
```cypher
UNWIND [
{ name: "田中太郎", type: "Person", observations: ["制御設計:5", "業務自動化:4", "Excel処理:5", "RPA:3", "ソフトウェア設計:4", "テスト計画:4", "仕様策定:5", "ファイル入出力:3", "バックエンド:2", "レビュー:5"] },
{ name: "佐藤花子", type: "Person", observations: ["文書デジタル化:5", "データベース設計:5", "クラウド運用:4", "AI検索:4", "REST API設計:4", "フロントエンド:4", "Redux:3", "PowerAutomate:2", "CI/CD:2", "ナレッジ共有:3"] },
{ name: "鈴木健一", type: "Person", observations: ["Matlab:5", "数値計算:5", "データ可視化:3", "C#:3", "Python:3", "システム連携:4", "クラウド実装:3", "テスト自動化:4", "設計パターン:3", "Azure:3", "DevOps:2"] },
{ name: "山本美咲", type: "Person", observations: ["走行制御:5", "ベクトル検索:4", "Python:3", "API設計:4", "ExcelVBA:4", "テスト設計:5", "ロジック設計:4", "品質保証:3", "UI/UX:2", "コラボレーション:3"] },
{ name: "高橋悟", type: "Person", observations: ["マルチエージェント:5", "UI設計:4", "DX:4", "アジャイル:4", "プロジェクト管理:4", "scrum:3", "Redux:3", "ワークフロー設計:3", "フロントエンド開発:4", "ワークショップファシリテーション:3", "チームビルディング:3"] },
{ name: "中村彩", type: "Person", observations: ["データパイプライン:5", "AI検索:4", "データ変換:4", "API統合:3", "ステークホルダー調整:3", "業務自動化:4", "DevOps:3", "フレームワーク選定:2", "品質管理:3"] },
{ name: "小林大地", type: "Person", observations: ["マルチエージェント:4", "UI設計:3", "テスト計画:3", "画面設計:4", "ドキュメント化:3", "ワークフロー改善:3"] },
{ name: "松本恵", type: "Person", observations: ["走行制御:4", "AI活用:3", "データ分析:4", "Excel自動化:4", "API設計:4", "テスト自動化:3", "バックエンド:3", "品質保証:2", "パフォーマンス改善:3"] },
{ name: "渡辺光", type: "Person", observations: ["文書デジタル化:5", "AI応用:4", "機械学習:4", "日本語NLP:5", "DB設計:2", "PowerAutomate:3", "Python:3", "業務効率化:4", "データラベリング:3", "チーム教育:3"] },
{ name: "加藤優", type: "Person", observations: ["DB設計:4", "バックエンド:3", "Redux:2", "JavaScript:4", "自動テスト:3", "設計レビュー:2"] },
{ name: "石川絵里", type: "Person", observations: ["データ整形:3", "データパイプライン:3", "Excel操作:5", "日本語NLP:4", "フロントエンド開発:2", "テスト設計:3", "業務最適化:3"] },
{ name: "村上直樹", type: "Person", observations: ["Excel処理:5", "制御設計:4", "コーディング規約:4", "レビュー:4", "動作テスト:3", "バックエンド:3", "Python:3"] },
{ name: "斎藤 航", type: "Person", observations: ["プロジェクト管理:5", "AIモデル開発:4", "仕様書策定:4", "業務改革:3", "R&Dマネジメント:3"] },
{ name: "山田みき", type: "Person", observations: ["クラウド:4", "コラボレーション:3", "DB運用:5", "AI活用:4", "オペレーション改善:3"] },
{ name: "藤本剛", type: "Person", observations: ["ファイル処理:5", "ExcelVBA:5", "業務最適化:3", "コーディングレビュー:4", "テスト支援:3", "標準化:3", "バックエンド:3"] },
{ name: "三浦真理子", type: "Person", observations: ["仕様策定:4", "UI設計:4", "会議ファシリテート:3", "問題分析:4", "Excel操作:3"] }
] AS person
CREATE (p:Person { name: person.name, type: person.type })
WITH p, person.observations AS obs
UNWIND obs AS ob
MERGE (o:Observation { value: ob })
MERGE (p)-[:HAS_OBSERVATION]->(o);
```

2. domains.cypher
```cypher
UNWIND [
{ name: "制御設計", type: "Domain" },
{ name: "業務自動化", type: "Domain" },
{ name: "Excel処理", type: "Domain" },
{ name: "RPA", type: "Domain" },
{ name: "ソフトウェア設計", type: "Domain" },
{ name: "テスト計画", type: "Domain" },
{ name: "仕様策定", type: "Domain" },
{ name: "ファイル入出力", type: "Domain" },
{ name: "バックエンド", type: "Domain" },
{ name: "レビュー", type: "Domain" },
{ name: "文書デジタル化", type: "Domain" },
{ name: "データベース設計", type: "Domain" },
{ name: "クラウド運用", type: "Domain" },
{ name: "AI検索", type: "Domain" },
{ name: "REST API設計", type: "Domain" },
{ name: "フロントエンド", type: "Domain" },
{ name: "Redux", type: "Domain" },
{ name: "PowerAutomate", type: "Domain" },
{ name: "CI/CD", type: "Domain" },
{ name: "ナレッジ共有", type: "Domain" },
{ name: "Matlab", type: "Domain" },
{ name: "数値計算", type: "Domain" },
{ name: "データ可視化", type: "Domain" },
{ name: "C#", type: "Domain" },
{ name: "Python", type: "Domain" },
{ name: "システム連携", type: "Domain" },
{ name: "クラウド実装", type: "Domain" },
{ name: "テスト自動化", type: "Domain" },
{ name: "設計パターン", type: "Domain" },
{ name: "Azure", type: "Domain" },
{ name: "DevOps", type: "Domain" },
{ name: "走行制御", type: "Domain" },
{ name: "ベクトル検索", type: "Domain" },
{ name: "API設計", type: "Domain" },
{ name: "ExcelVBA", type: "Domain" },
{ name: "テスト設計", type: "Domain" },
{ name: "ロジック設計", type: "Domain" },
{ name: "品質保証", type: "Domain" },
{ name: "UI/UX", type: "Domain" },
{ name: "コラボレーション", type: "Domain" },
{ name: "マルチエージェント", type: "Domain" },
{ name: "UI設計", type: "Domain" },
{ name: "DX", type: "Domain" },
{ name: "アジャイル", type: "Domain" },
{ name: "プロジェクト管理", type: "Domain" },
{ name: "scrum", type: "Domain" },
{ name: "ワークフロー設計", type: "Domain" },
{ name: "フロントエンド開発", type: "Domain" },
{ name: "ワークショップファシリテーション", type: "Domain" },
{ name: "チームビルディング", type: "Domain" },
{ name: "データパイプライン", type: "Domain" },
{ name: "データ変換", type: "Domain" },
{ name: "API統合", type: "Domain" },
{ name: "ステークホルダー調整", type: "Domain" },
{ name: "フレームワーク選定", type: "Domain" },
{ name: "品質管理", type: "Domain" },
{ name: "画面設計", type: "Domain" },
{ name: "ドキュメント化", type: "Domain" },
{ name: "ワークフロー改善", type: "Domain" },
{ name: "AI活用", type: "Domain" },
{ name: "データ分析", type: "Domain" },
{ name: "Excel自動化", type: "Domain" },
{ name: "パフォーマンス改善", type: "Domain" },
{ name: "AI応用", type: "Domain" },
{ name: "機械学習", type: "Domain" },
{ name: "日本語NLP", type: "Domain" },
{ name: "DB設計", type: "Domain" },
{ name: "業務効率化", type: "Domain" },
{ name: "データラベリング", type: "Domain" },
{ name: "チーム教育", type: "Domain" },
{ name: "JavaScript", type: "Domain" },
{ name: "自動テスト", type: "Domain" },
{ name: "設計レビュー", type: "Domain" },
{ name: "データ整形", type: "Domain" },
{ name: "Excel操作", type: "Domain" },
{ name: "フロントエンド開発", type: "Domain" },
{ name: "業務最適化", type: "Domain" },
{ name: "コーディング規約", type: "Domain" },
{ name: "動作テスト", type: "Domain" },
{ name: "AIモデル開発", type: "Domain" },
{ name: "仕様書策定", type: "Domain" },
{ name: "業務改革", type: "Domain" },
{ name: "R&Dマネジメント", type: "Domain" },
{ name: "クラウド", type: "Domain" },
{ name: "DB運用", type: "Domain" },
{ name: "オペレーション改善", type: "Domain" },
{ name: "ファイル処理", type: "Domain" },
{ name: "業務最適化", type: "Domain" },
{ name: "コーディングレビュー", type: "Domain" },
{ name: "テスト支援", type: "Domain" },
{ name: "標準化", type: "Domain" },
{ name: "会議ファシリテート", type: "Domain" },
{ name: "問題分析", type: "Domain" }
] AS domain
CREATE (:Domain { name: domain.name, type: domain.type });
```

3. relations.cypher
```cypher
UNWIND [
{ relationType: "RELATES_TO", source: "制御設計", target: "ソフトウェア設計" },
{ relationType: "RELATES_TO", source: "Excel処理", target: "ファイル入出力" },
{ relationType: "RELATES_TO", source: "Excel処理", target: "ExcelVBA" },
{ relationType: "RELATES_TO", source: "RPA", target: "業務自動化" },
{ relationType: "RELATES_TO", source: "データベース設計", target: "DB運用" },
{ relationType: "RELATES_TO", source: "PowerAutomate", target: "業務自動化" },
{ relationType: "RELATES_TO", source: "データ可視化", target: "数値計算" },
{ relationType: "RELATES_TO", source: "Matlab", target: "数値計算" },
{ relationType: "RELATES_TO", source: "Python", target: "機械学習" },
{ relationType: "RELATES_TO", source: "Python", target: "データパイプライン" },
{ relationType: "RELATES_TO", source: "テスト設計", target: "テスト計画" },
{ relationType: "RELATES_TO", source: "設計レビュー", target: "レビュー" },
{ relationType: "RELATES_TO", source: "フロントエンド", target: "UI設計" },
{ relationType: "RELATES_TO", source: "フロントエンド開発", target: "Redux" },
{ relationType: "RELATES_TO", source: "フロントエンド", target: "バックエンド" },
{ relationType: "RELATES_TO", source: "REST API設計", target: "API統合" },
{ relationType: "RELATES_TO", source: "DX", target: "業務改革" },
{ relationType: "RELATES_TO", source: "クラウド", target: "クラウド運用" },
{ relationType: "RELATES_TO", source: "CI/CD", target: "DevOps" },
{ relationType: "RELATES_TO", source: "AI検索", target: "日本語NLP" },
{ relationType: "RELATES_TO", source: "AIモデル開発", target: "機械学習" },
{ relationType: "RELATES_TO", source: "UI設計", target: "UX" },
{ relationType: "RELATES_TO", source: "scrum", target: "アジャイル" },
{ relationType: "RELATES_TO", source: "プロジェクト管理", target: "チームビルディング" },
{ relationType: "RELATES_TO", source: "レビュー", target: "標準化" },
{ relationType: "RELATES_TO", source: "データ変換", target: "データ整形" },
{ relationType: "RELATES_TO", source: "データパイプライン", target: "データ変換" },
{ relationType: "RELATES_TO", source: "AI検索", target: "データ分析" },
{ relationType: "RELATES_TO", source: "ExcelVBA", target: "Excel自動化" },
{ relationType: "RELATES_TO", source: "DB設計", target: "クラウド" },
{ relationType: "RELATES_TO", source: "UI設計", target: "画面設計" }
] AS rel
MATCH (s { name: rel.source })
MATCH (t { name: rel.target })
MERGE (s)-[r:RELATES_TO]->(t);
```

4. observations.cypher
```cypher
UNWIND [
{ entityName: "田中太郎", contents: ["制御設計:5", "業務自動化:4", "Excel処理:5", "RPA:3", "ソフトウェア設計:4", "テスト計画:4", "仕様策定:5", "ファイル入出力:3", "バックエンド:2", "レビュー:5"] },
{ entityName: "佐藤花子", contents: ["文書デジタル化:5", "データベース設計:5", "クラウド運用:4", "AI検索:4", "REST API設計:4", "フロントエンド:4", "Redux:3", "PowerAutomate:2", "CI/CD:2", "ナレッジ共有:3"] },
{ entityName: "鈴木健一", contents: ["Matlab:5", "数値計算:5", "データ可視化:3", "C#:3", "Python:3", "システム連携:4", "クラウド実装:3", "テスト自動化:4", "設計パターン:3", "Azure:3", "DevOps:2"] },
{ entityName: "山本美咲", contents: ["走行制御:5", "ベクトル検索:4", "Python:3", "API設計:4", "ExcelVBA:4", "テスト設計:5", "ロジック設計:4", "品質保証:3", "UI/UX:2", "コラボレーション:3"] },
{ entityName: "高橋悟", contents: ["マルチエージェント:5", "UI設計:4", "DX:4", "アジャイル:4", "プロジェクト管理:4", "scrum:3", "Redux:3", "ワークフロー設計:3", "フロントエンド開発:4", "ワークショップファシリテーション:3", "チームビルディング:3"] },
{ entityName: "中村彩", contents: ["データパイプライン:5", "AI検索:4", "データ変換:4", "API統合:3", "ステークホルダー調整:3", "業務自動化:4", "DevOps:3", "フレームワーク選定:2", "品質管理:3"] },
{ entityName: "小林大地", contents: ["マルチエージェント:4", "UI設計:3", "テスト計画:3", "画面設計:4", "ドキュメント化:3", "ワークフロー改善:3"] },
{ entityName: "松本恵", contents: ["走行制御:4", "AI活用:3", "データ分析:4", "Excel自動化:4", "API設計:4", "テスト自動化:3", "バックエンド:3", "品質保証:2", "パフォーマンス改善:3"] },
{ entityName: "渡辺光", contents: ["文書デジタル化:5", "AI応用:4", "機械学習:4", "日本語NLP:5", "DB設計:2", "PowerAutomate:3", "Python:3", "業務効率化:4", "データラベリング:3", "チーム教育:3"] },
{ entityName: "加藤優", contents: ["DB設計:4", "バックエンド:3", "Redux:2", "JavaScript:4", "自動テスト:3", "設計レビュー:2"] },
{ entityName: "石川絵里", contents: ["データ整形:3", "データパイプライン:3", "Excel操作:5", "日本語NLP:4", "フロントエンド開発:2", "テスト設計:3", "業務最適化:3"] },
{ entityName: "村上直樹", contents: ["Excel処理:5", "制御設計:4", "コーディング規約:4", "レビュー:4", "動作テスト:3", "バックエンド:3", "Python:3"] },
{ entityName: "斎藤 航", contents: ["プロジェクト管理:5", "AIモデル開発:4", "仕様書策定:4", "業務改革:3", "R&Dマネジメント:3"] },
{ entityName: "山田みき", contents: ["クラウド:4", "コラボレーション:3", "DB運用:5", "AI活用:4", "オペレーション改善:3"] },
{ entityName: "藤本剛", contents: ["ファイル処理:5", "ExcelVBA:5", "業務最適化:3", "コーディングレビュー:4", "テスト支援:3", "標準化:3", "バックエンド:3"] },
{ entityName: "三浦真理子", contents: ["仕様策定:4", "UI設計:4", "会議ファシリテート:3", "問題分析:4", "Excel操作:3"] }
] AS obsdata
MATCH (p:Person { name: obsdata.entityName })
UNWIND obsdata.contents AS ob
MERGE (o:Observation { value: ob })
MERGE (p)-[:HAS_OBSERVATION]->(o);
```

## 2. docker-composeでNeo4jを立てます
docker-compose.ymlを定義します。

```yaml
services:
  neo4j:
    image: neo4j:latest
    volumes:
      - /$HOME/neo4j/logs:/logs
      - /$HOME/neo4j/config:/config
      - /$HOME/neo4j/data:/data
      - /$HOME/neo4j/plugin:/plugins
      - ./import:/import
    environment:
      - NEO4J_AUTH_FILE=/run/secrets/neo4j_auth_file
    ports:
      - "7474:7474"
      - "7687:7687"
    restart: always
    secrets:
      - neo4j_auth_file
secrets:
  neo4j_auth_file:
    file: ./neo4j_auth.txt
```

neo4j_auth.txtは、以下のように定義します。
```
neo4j/mypassword
```

Neo4j コンテナを起動します。
```bash
docker compose up -d
```
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-12-55.png)

## 3. Neo4jにデータを登録します

コンテナが起動したら、Neo4jのコンテナに接続します。
```bash
docker exec -it neo4j-container-neo4j-1 /bin/bash
```

Cypher ShellでCypherクエリを実行します。
```bash
cat /import/persons.cypher | cypher-shell -u neo4j -p mypassword
cat /import/domains.cypher | cypher-shell -u neo4j -p mypassword
cat /import/relations.cypher | cypher-shell -u neo4j -p mypassword
cat /import/observations.cypher | cypher-shell -u neo4j -p mypassword
```

問題なく登録されているか確認します。
```bash
cypher-shell -u neo4j -p mypassword "MATCH (n) RETURN n LIMIT 50;"
```

## 4. VSCodeのGitHubCopilot ChatでのMCPサーバ準備
.vscodeフォルダ内に、mcp.jsonを作成します。
```json
{
  "servers": {
    "neo4j": {
      "command": "uvx",
      "args": [
        "mcp-neo4j-memory@0.1.4",
        "--db-url",
        "neo4j://localhost:7687",
        "--username",
        "neo4j",
        "--password",
        "mypassword"
      ]
    }
  }
}
```

Startボタンが表示されるのでクリックしてMCPサーバを起動します。
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-16-06.png)

MCPサーバが起動したら、CopilotをAgentモードにします。
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-17-12.png)

ツールアイコンを押下して、Neo4jのMCPServerが存在するか確認します。
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-17-38.png)

![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-18-13.png)

## 5. 自然言語で問い合わせてみましょう！！！

さて、それでは問い合わせてみましょう。
Outputは文字化けしてしまってますが、ご容赦ください。。

「**DB設計に得意な人を探して**」
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-20-07.png)

「**データベースの設計をしたことがある人はだれ？**」
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-20-48.png)

「**AIの投資領域を担当できそうな人はだれ？**」
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-22-14.png)

「**Azureでのアプリ開発案件にアサインできそうな人はだれ？**」
![](/images/neo4j-mcp-person-knowledge/2025-06-18-22-24-15.png)

なかなかに柔軟な検索と回答をしてくれています。

# まとめ
Neo4jのMCPを使うことで、グラフデータベースに登録された情報を自然言語で問い合わせることができました。
このように、MCPを使うことで、グラフデータベースの情報をより直感的に扱うことができるようになります。
グラフデータベースのクエリを知らなくてもよいので、開発者以外の人でも使いやすいです。