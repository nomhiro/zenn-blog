---
title: "StreamlitでMermaidのマインドマップを表示する"
emoji: "🕌"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["streamlit", "mermaid", "mindmap", "html", "javascript"]
published: true
---

# はじめに
MarkdownのMermaidを使ってマインドマップを描画することができます。
![](/images/streamlit-mermaid-maindmap/2025-07-29-13-54-58.png)

これを、Streamlitのアプリで表示したかったので、
StreamlitのHTML埋め込み機能を使って、クライアントサイドのMermaid.jsライブラリでマインドマップを描画します。

- Streamlit - Pythonベースのウェブアプリフレームワーク
- Mermaid.js - テキストベースでダイアグラムを生成するJavaScriptライブラリ
- HTML Components - StreamlitのカスタムHTMLコンポーネント機能

# 実装コード

```python
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mermaid Mindmap Viewer", layout="wide")

st.title("Mermaid形式マインドマップビューア")

# Mermaidコード
mermaid_code = st.text_area(
    "Mermaidコードを入力してください",
    value="""mindmap
  root((中心テーマ))
    起源
      ロングテール
      ::icon(fa fa-book)
      ポピュラリゼーション
        British popular psychology author Tony Buzan
    研究
      論文発表
        The effectiveness of mind mapping
      ツール
        Pen and paper
        Mermaid
    クリエイティブ用途
      ::icon(fa fa-lightbulb)
      ブレインストーミング
      アート
        色彩
        図形
    開発ツール
      プログラミング
        設計
        ドキュメント
      プロジェクト管理
""",
    height=300
)

if st.button("マインドマップを表示"):
    mermaid_html = f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </head>
    <body>
        <div class="mermaid">
        {mermaid_code}
        </div>
    </body>
    </html>
    """
    
    components.html(mermaid_html, height=600, scrolling=True)

st.markdown("---")
st.markdown("### 使い方")
st.markdown("1. 上のテキストエリアにMermaid形式のマインドマップコードを入力")
st.markdown("2. 「マインドマップを表示」ボタンをクリック")
st.markdown("3. 下にマインドマップが表示されます")
```

このように表示されます。

![](/images/streamlit-mermaid-maindmap/2025-07-29-13-46-37.png)


以上です！

リポジトリはこちらです。
https://github.com/nomhiro/streamlit-mermaid-maindmap