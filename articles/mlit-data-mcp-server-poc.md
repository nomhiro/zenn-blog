---
title: "国土交通データプラットフォームMCPサーバーを使って建設業界でAI活用！🏗️"
emoji: "🏗️"
type: "tech"
topics: ["mcp", "llm", "GraphQL", "mlit", "Claude"]
published: true
---

![](/images/mlit-data-mcp-server-poc/2026-01-20-23-15-30.png)

# はじめに
2026年は、AIエージェントが今まで以上に組織に浸透し、人とAIの協働のための組織化、環境整備、ガバナンスが進んでいく年になりそうです。（そうしたい）

AIエージェントは、プロンプトとツールによって成り立ちます。ツールという観点だと、MCP（Model Context Protocol）は、AIエージェントが外部データやサービスにアクセスするための標準的なインターフェースを提供するプロトコルです。

そんな中、 **国土交通データプラットフォームMCPサーバー（α版）** が2025年にGitHubで公開されました。このMCPサーバーは、国土交通省が提供する国土交通データプラットフォーム（国交DPF）に格納された多様なデータセットに対して、自然言語での対話を通じてアクセスできるように設計されています。

本記事では、このMCPサーバーで取得できるデータを詳しく調査し、建設業界における具体的なユースケースを考えてみます。

:::message alert
わたし自身は建設業界のドメイン知識に乏しいため、ユースケースの妥当性についてはあっていない場合があります。あくまでMCPサーバーの活用イメージを掴むための参考として参照ください。
:::

# 国土交通データプラットフォームとは

国土交通データプラットフォーム（国交DPF）は、国土交通省が2020年4月に公開したデータ基盤です。以下の特徴を持っています。

- **データの一元化**: 国土・道路・河川・港湾・都市計画など多分野のデータを横断検索可能
- **デジタルツイン**: フィジカル空間をサイバー空間に再現
- **3次元データ視覚化**: BIM/CIMモデルや点群データを3D地図上で表示
- **オープンAPI**: 外部システムとの連携が可能

従来、これらのデータを取得するには複数のWebサイトを巡回し、APIの仕様を理解する必要がありました。しかしMCPサーバーを使うことで、**自然言語での対話を通じて直感的にデータを検索・取得**できるようになります。

## MCPサーバーの主な機能

国土交通データプラットフォームMCPサーバーは、以下の17種類のツールを提供しています。
ツールを使う流れは、検索機能を持ったツールでデータを絞り込み、データ取得機能で詳細情報を取得する形になります。

### 検索機能

| ツール名 | 説明 |
|---------|------|
| `search` | キーワードによるデータ検索（並べ替え・件数指定可能） |
| `search_by_location_rectangle` | 矩形範囲での空間検索 |
| `search_by_location_point_distance` | 指定地点からの円形範囲検索 |
| `search_by_attribute` | カタログ名・データセット名・都道府県・市区町村での属性検索 |

### データ取得機能

| ツール名 | 説明 |
|---------|------|
| `get_data` | データの詳細情報を取得 |
| `get_data_summary` | データの基本情報（ID・タイトル）を取得 |
| `get_data_catalog` | データカタログ・データセットの詳細情報を取得 |
| `get_data_catalog_summary` | カタログの基本情報を取得 |
| `get_all_data` | 条件に一致する大量データを一括取得 |
| `get_count_data` | 条件に一致するデータ件数を取得 |

### ファイル・メディア取得

| ツール名 | 説明 |
|---------|------|
| `get_file_download_urls` | ファイルのダウンロードURL取得（有効期限60秒） |
| `get_zipfile_download_url` | 複数ファイルをZIP形式でダウンロード |
| `get_thumbnail_urls` | サムネイル画像のURL取得 |

### 補助機能

| ツール名 | 説明 |
|---------|------|
| `get_suggest` | キーワード候補の取得 |
| `get_prefecture_data` | 都道府県名・コード一覧 |
| `get_municipality_data` | 市区町村名・コード一覧 |
| `get_mesh` | メッシュコード指定でのデータ取得 |
| `normalize_codes` | 都道府県名・市区町村名の正規化 |

## 取得できるデータの種類

国交DPFには、以下の分野のデータベースが連携されています。

### インフラ関連データ

- **橋梁データ**: 全国の橋梁諸元、点検データ（全国道路施設点検データベース）
- **トンネルデータ**: トンネルの構造・点検情報
- **ダム・河川構造物**: 水門、堰、ダムの諸元情報
- **道路データ**: 道路台帳、工事実績情報、設計図面

### 地盤・地質データ

- **ボーリングデータ**: 全国のボーリング柱状図、土質試験結果
- **地盤情報**: 国土地盤情報検索サイトとの連携

### 3Dモデル・BIM/CIM

- **BIM/CIMモデル**: IFC形式の3次元モデル
- **3D都市モデル（PLATEAU）**: CityGML形式の都市モデル
- **点群データ**: レーザー測量による3次元点群

### 災害・防災関連

- **浸水想定区域**: 洪水・高潮・津波の浸水想定
- **自然災害伝承碑**: 過去の災害記録
- **ハザードマップ情報**

### その他

- **電子納品成果品**: 工事・業務の電子成果品
- **航空写真**: 国土地理院の空中写真
- **都市計画情報**: 用途地域、都市計画道路

# セットアップ方法

### 前提条件

- Python 3.10以上
- Claude Desktop（または他のMCP対応AIアプリケーション）
- 国土交通データプラットフォームのAPIキー

### 手順

#### 1. APIキーの取得

[国土交通データプラットフォーム](https://www.mlit-data.jp/)でアカウントを作成し、APIキーを取得します。

#### 2. リポジトリのクローン

```bash
git clone https://github.com/MLIT-DATA-PLATFORM/mlit-dpf-mcp.git
cd mlit-dpf-mcp
```

#### 3. 仮想環境の作成

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

#### 4. 依存ライブラリのインストール

```bash
pip install -e .
pip install aiohttp pydantic tenacity python-json-logger mcp python-dotenv
```

#### 5. 環境変数の設定

`.env.example`をコピーして`.env`を作成：

```bash
MLIT_API_KEY=your_api_key_here
MLIT_BASE_URL=https://www.mlit-data.jp/api/v1/
```

#### 6. Claude Desktopの設定

`claude_desktop_config.json`にMCPサーバーを追加：

```json
{
  "mcpServers": {
    "mlit-dpf-mcp": {
      "command": "path/to/mlit-dpf-mcp/.venv/Scripts/python.exe",
      "args": [
        "path/to/mlit-dpf-mcp/src/server.py"
      ],
      "env": {
        "MLIT_API_KEY": "your_api_key_here",
        "MLIT_BASE_URL": "https://www.mlit-data.jp/api/v1/",
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

#### 7. Claude Desktopを再起動

設定後、Claude Desktopを再起動すると、国交DPFのツールが利用可能になります。


## 建設業界でのユースケース

### ユースケース1: 現場調査の事前準備自動化

**課題**: 新規工事の現場調査前に、周辺のインフラ情報や地盤情報を収集するのに数日かかる

**解決策**: AIアシスタントに「〇〇市△△町周辺のボーリングデータと既存橋梁情報を教えて」と指示するだけで、必要な情報を即座に取得

Claudeで実行した場合、以下のように位置情報からポーリングデータの検索や関連する情報を能動的にデータ取得します。

```txt
名古屋市中区周辺半径500mのボーリングデータを検索して。
最終的には詳細情報を調べてうえで、docxスキルを使ってレポートにして。
```

![](/images/mlit-data-mcp-server-poc/2026-01-20-21-28-49.png)

![](/images/mlit-data-mcp-server-poc/2026-01-20-21-29-18.png)

![](/images/mlit-data-mcp-server-poc/2026-01-20-21-29-41.png)

![](/images/mlit-data-mcp-server-poc/2026-01-20-21-32-19.png)

検索した詳細データから、docxスキル（Wordファイル生成スキル）を使って、調査報告書のドラフトを自動生成してもらいます。

![](/images/mlit-data-mcp-server-poc/2026-01-20-22-17-33.png)

### ユースケース2: 入札前の類似工事実績調査

**課題**: 入札参加にあたり、類似工事の実績や技術資料を調べるのに時間がかかる

**解決策**: キーワード検索と属性検索を組み合わせ、特定地域・工種の過去工事データを効率的に収集

```txt
愛知県内の橋梁補修工事の電子納品データを検索して、過去3年分の工事概要を整理してください。
最終的には詳細情報を調べてうえで、docxスキルを使ってレポートにして。
```

まずは検索ツールで工事データを検索します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-20-45.png)

検索できたら、get_dataツールで詳細情報を取得します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-22-31.png)

最後に、docxスキルで提案書ドラフトを生成します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-25-28.png)

![](/images/mlit-data-mcp-server-poc/2026-01-20-22-27-08.png)

### ユースケース3: BIM/CIMモデルの参照データ収集

**課題**: BIM/CIMモデル作成時に必要な周辺地形・既存構造物のデータ収集が煩雑

**解決策**: 空間検索で対象エリアの3Dモデル、地形データ、既存構造物データを一括取得

```txt
木曽川橋の3D地形データとPLATEAUの建物モデルをダウンロードできるURLを知りたい。
```

対象の橋のデータ収集が能動的に行われます。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-34-23.png)

データを特定すると、data_idを指定して、get_file_download_urlsツールでダウンロードURLを取得します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-35-15.png)

最終的に、PLATEAUの3D地形データのZIPファイルのダウンロードURLを取得できました。
ちなみに、URLはちゃんと正しいURLで、ZIPファイルをダウンロードできました。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-37-20.png)

3DモデルのためのデータのURLも教えてくれます。
![](/images/mlit-data-mcp-server-poc/2026-01-20-22-38-28.png)

### ユースケース4: インフラ老朽化診断の支援

**課題**: 維持管理計画策定のため、管理施設の点検データを横断的に分析したい

**解決策**: 点検データベースと連携し、経年劣化の傾向分析や優先補修箇所の特定を支援

```
各務原市管内の橋梁で、点検結果が「III（早期措置段階）」以上のものを取得し、詳細情報を調べたうえでdocxスキルを使ってレポートにして。
```

まず、各務原市の市町村コードをもとに、橋梁データを検索します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-23-04-53.png)

次に、点検結果の詳細情報を取得します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-23-05-38.png)

詳細情報を収集しながら、docxスキルでレポートを生成します。
![](/images/mlit-data-mcp-server-poc/2026-01-20-23-07-21.png)

![](/images/mlit-data-mcp-server-poc/2026-01-20-23-09-53.png)

![](/images/mlit-data-mcp-server-poc/2026-01-20-23-10-07.png)


## 活用のポイント

### 1. 空間検索を活用する

特定地点周辺のデータを効率的に取得するには、`search_by_location_point_distance`や`search_by_location_rectangle`が有効です。緯度・経度を指定することで、ピンポイントで必要なデータを取得できます。

### 2. 属性検索で絞り込む

`search_by_attribute`を使えば、都道府県・市区町村単位での絞り込みが可能です。大量のデータから必要なものだけを抽出する際に便利です。

### 3. バルク取得で効率化

`get_all_data`を使えば、条件に一致するデータを一括取得できます。レポート作成や分析用途に適しています。

### 4. サジェスト機能の活用

適切なキーワードが分からない場合は、`get_suggest`でキーワード候補を取得できます。

## まとめ

建設業界では2024年からBIM/CIMが原則適用となり、デジタルデータの活用がより一層重要になっています。
個人的には、こういったデータ取得するツールを活用することで、AIの活用を伸ばせる領域かもしれません。

## 参考リンク

- [国土交通データプラットフォームMCPサーバー（GitHub）](https://github.com/MLIT-DATA-PLATFORM/mlit-dpf-mcp)
- [国土交通データプラットフォーム](https://www.mlit-data.jp/)
- [国土交通省 技術調査課](https://www.mlit.go.jp/tec/tec_tk_000066.html)
- [MCP（Model Context Protocol）](https://modelcontextprotocol.io/)
- [BIM/CIMポータルサイト](https://www.nilim.go.jp/lab/qbg/bimcim/)
