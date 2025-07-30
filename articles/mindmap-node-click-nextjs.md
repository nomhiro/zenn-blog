---
title: "Mermaid.jsでクリック可能なマインドマップを実装する（Next.js）"
emoji: "🕌"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["mermaid", "mindmap", "nextjs", "typescript", "react"]
published: false
---

# はじめに

こちらの記事では StreamlitでMermaidのマインドマップを表示しました。
https://zenn.dev/nomhiro/articles/streamlit-mermaid-maindmap

今回は、マインドマップのノードをクリックしたらノード情報を詳細表示するようにしたいと思います。
結論、このようになります。
ノードをクリックすると、右側Sidebarにそのノードの詳細情報が表示されます。
![](/images/mindmap-node-click-nextjs/chrome-capture-2025-07-30.gif)

# （課題）Streamlitでのクリックイベント問題

Streamlitの`components.html()`でMermaidを表示する方法では、SVG要素のクリックイベントを取得することができませんでした。

```python
# Streamlitでの表示方法
components.html(mermaid_html, height=400)
# → 実際にはiframe内に描画される
```

Streamlitは`components.html()`でHTMLコンテンツを表示する際、**iframe**を使用しますが、制約があります。
- ❌ iframe内のクリックイベントを親ページ（Streamlit）に送れない
- ❌ セキュリティ上、異なる環境間の通信が制限される
- ❌ Python側でJavaScriptイベントを受け取る仕組みがない


# Streamlitはやめました（Next.jsでの実装に変更）

以下の技術スタックで実現します。
```
- フレームワーク: Next.js 14 (App Router)
- 描画ライブラリ: Mermaid.js
- 状態管理: Zustand  
- スタイリング: Tailwind CSS
- 言語: TypeScript
```

リポジトリはこちらです。
https://github.com/nomhiro/mindmap-node-click-nextjs

### ディレクトリ構成
```
/src
  /app
    page.tsx                 # メインページ
  /components  
    MermaidRenderer.tsx      # Mermaid描画コンポーネント
    MermaidEditor.tsx        # テキスト入力エディタ
    DetailsSidebar.tsx       # 詳細表示サイドバー
  /store
    mindmapStore.ts          # Zustand状態管理
  /lib
    mermaidParser.ts         # Mermaidパーサー
  /types
    mindmap.ts              # TypeScript型定義
```

## Mermaid描画コンポーネント（MermaidRenderer）

### 1. Mermaidの初期化と描画

```typescript
'use client';

import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import { useMindmapStore } from '@/store/mindmapStore';

/**
 * MermaidRendererコンポーネント
 * 
 * Mermaid.js形式のマインドマップを描画し、ノードクリックイベントを処理する
 * Next.jsのApp RouterでクライアントサイドレンダリングとしてMermaidを活用
 * 
 * @param {Object} props - コンポーネントのプロパティ
 * @param {string} props.mermaidCode - 描画するMermaid形式のコード文字列
 * @returns {JSX.Element} Mermaidで描画されたマインドマップ
 */
export default function MermaidRenderer({ mermaidCode }: { mermaidCode: string }) {
  // SVGコンテナへの参照を保持
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Zustandストアから状態管理関数を取得
  // setSelectedNode: クリックされたノードを設定する関数
  // parseMermaidForNodeData: Mermaidコードを解析してノードデータを生成する関数
  const { setSelectedNode, parseMermaidForNodeData } = useMindmapStore();

  /**
   * Mermaid.jsの初期設定
   * コンポーネントマウント時に一度だけ実行される
   */
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,          // 自動レンダリングを無効化（手動制御のため）
      theme: 'default',            // デフォルトテーマを使用
      securityLevel: 'loose',      // HTML/JSの埋め込みを許可（クリックイベント用）
      fontFamily: 'Arial, sans-serif',
      mindmap: {
        padding: 20,               // マインドマップ内の余白
        maxNodeSizeRatio: 0.5      // ノードの最大サイズ比率
      }
    });
  }, []);
```

### 2. 動的レンダリングとイベント追加

```typescript
  /**
   * Mermaidコードが変更されたときの再レンダリング処理
   * 
   * 1. Mermaid.jsでSVGを生成
   * 2. SVGをDOMに挿入
   * 3. ノードデータを解析してストアに保存
   * 4. クリックイベントリスナーを追加
   */
  useEffect(() => {
    // コンテナが存在しない、またはMermaidコードが空の場合は処理をスキップ
    if (!containerRef.current || !mermaidCode.trim()) return;

    /**
     * 非同期でMermaidを描画する内部関数
     */
    const renderMermaid = async () => {
      try {
        // 一意なIDを生成（Mermaidの内部処理で必要）
        const id = `mermaid-${Date.now()}`;
        
        // Mermaid.jsでコードをSVGに変換
        // render関数は{ svg: string }形式のオブジェクトを返す
        const { svg } = await mermaid.render(id, mermaidCode);
        
        // コンテナが存在する場合のみ処理を継続（非同期処理中にアンマウントされる可能性があるため）
        if (containerRef.current) {
          // 生成されたSVGをコンテナに挿入
          containerRef.current.innerHTML = svg;
          
          // Mermaidコードを解析してノード情報をストアに保存
          parseMermaidForNodeData(mermaidCode);
          
          // SVG内のノードにクリックイベントを追加
          addClickEventListeners();
        }
      } catch (error) {
        // Mermaid構文エラーなどをコンソールに出力
        console.error('Mermaid rendering error:', error);
      }
    };

    renderMermaid();
  }, [mermaidCode, parseMermaidForNodeData]);
```

### 3. SVGノードへのクリックイベント追加

```typescript
  /**
   * SVG内のノード要素にクリックイベントリスナーを追加する関数
   * 
   * Mermaid.jsが生成するSVGの構造は一定ではないため、
   * 複数のセレクタパターンでノード要素を検出する
   */
  const addClickEventListeners = () => {
    // コンテナが存在しない場合は処理を中断
    if (!containerRef.current) return;

    // Mermaidが生成する可能性のあるノード要素を全て取得
    // 以下のパターンでマッチング
    // - .mindmap-node: マインドマップ固有のクラス
    // - .node: 一般的なノードクラス  
    // - [id*="node"]: IDに"node"を含む要素
    // - [class*="node"]: クラスに"node"を含む要素
    const nodes = containerRef.current.querySelectorAll(
      '.mindmap-node, .node, [id*="node"], [class*="node"]'
    );
    
    // 各ノードにクリックイベントを追加
    nodes.forEach((node, index) => {
      // 重複してイベントリスナーを追加しないようにフラグをチェック
      // useEffectが複数回実行される可能性があるため、この防御処理が必要
      if ((node as any)._clickAdded) return;
      (node as any)._clickAdded = true;
      
      /**
       * ノードクリック時のイベントハンドラー
       */
      const handleClick = (event: Event) => {
        // デフォルトの動作（リンクジャンプなど）を防止
        event.preventDefault();
        // イベントの伝播を停止（親要素へのバブリングを防ぐ）
        event.stopPropagation();
        
        // ノード内のテキスト要素を探索
        // Mermaidのバージョンやダイアグラムタイプによって
        // text, span, divのいずれかにテキストが格納される
        const textElement = node.querySelector('text, span, div');
        const nodeText = textElement?.textContent?.trim() || `node_${index}`;
        
        // 選択されたノードをZustandストアに設定
        setSelectedNode(nodeText);
        
        // 選択状態のスタイルを適用
        // まず全ノードの選択状態をクリア
        nodes.forEach(n => n.classList.remove('selected'));
        // クリックされたノードに選択状態のクラスを追加
        node.classList.add('selected');
      };
      
      // クリックイベントリスナーを追加
      node.addEventListener('click', handleClick);
    });
  };
```

## 状態管理（ustand Store）

```typescript
import { create } from 'zustand';

/**
 * マインドマップアプリケーションの状態管理ストア
 * 
 * Zustandを使用して、以下の状態を管理
 * - マインドマップのデータ構造
 * - 選択されたノードのID
 * - Mermaidテキストエディタの入力内容
 */
export const useMindmapStore = create<MindmapStore>((set, get) => ({
  // パース済みのマインドマップデータ（ノードの階層構造を含む）
  mindmapData: null,
  
  // 現在選択されているノードのID
  selectedNodeId: null,
  
  // Mermaidエディタの初期値（サンプルデータ）
  mermaidInput: `mindmap
  root((中心テーマ))
    起源
      ロングテール
      ポピュラリゼーション
    研究
      論文発表
      ツール`,

  /**
   * 選択されたノードIDを更新する
   * @param nodeId - 選択されたノードのID（nullで選択解除）
   */
  setSelectedNode: (nodeId: string | null) => 
    set({ selectedNodeId: nodeId }),

  /**
   * Mermaidテキストを解析してマインドマップデータを生成・保存する
   * @param mermaidText - 解析対象のMermaid形式テキスト
   */
  parseMermaidForNodeData: (mermaidText: string) => {
    try {
      // MermaidParser.parseMindmap関数でテキストを解析
      // ノードの階層構造、親子関係、詳細情報などを抽出
      const mindmapData = MermaidParser.parseMindmap(mermaidText);
      
      // 解析結果をストアに保存
      set({ mindmapData });
    } catch (error) {
      // パース失敗時はエラーログを出力（UIには影響させない）
      console.error('Parsing error:', error);
    }
  }
}));
```

# まとめ

以下のことができております。

- **Mermaid.js native approach**を使ったマインドマップの描画
- **SVG DOM操作**によるクリックイベント取得

ナレッジグラフやフローチャートなど、他のMermaid図表にも対応できると思います。

![](/images/mindmap-node-click-nextjs/chrome-capture-2025-07-30.gif)

---

# （参考）試行錯誤の記録

### CSS Animation最適化の試行錯誤

**問題**: ホバー時のちらつき
```css
/* 重いアニメーション */
/* 複数のCSSプロパティを同時にアニメーションさせると、ちらつきの原因となる */
.node:hover {
  filter: brightness(1.1); 
  transform: scale(1.05); 
  transition: all 0.2s ease; 
}
```

1. **transform削除** → まだちらつく
2. **transition短縮** → 軽減するが完全解決せず  
3. **opacity使用** → 大幅改善
4. **animation完全無効化** → 解決

**最終解**
```css
.node:hover { 
  opacity: 0.8;  // opacityは軽量で、ちらつきを起こしにくい
}
.node * { 
  transition: none !important;  // 子要素のトランジションを完全に無効化
  animation: none !important;   // 子要素のアニメーションを完全に無効化
}
```

### ライブラリ選定の考慮事項

検討要素はこれらです。
- **学習コスト**: Mermaid < React Flow < D3.js
- **カスタマイズ性**: D3.js > React Flow > Mermaid
- **保守性**: Mermaid > React Flow > D3.js
- **要件適合度**: 元要件がMermaid形式だったためMermaidが最適