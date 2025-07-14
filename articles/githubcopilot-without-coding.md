---
title: "Codingだけじゃない！GitHub Copilotの活用法"
emoji: "💻"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["GitHub", "Copilot", "AI", "LLM"]
published: false
---

GitHub Copilotを、コーディング以外の用途にも使っているので、活用内容をまとめてみました。

# GitHub Copilotの活用法

## 1. 議事メモ、会話メモ
会議メモや、会話メモなどを、Markdown形式でまとめています。
プロジェクト、会議種類、日付でフォルダを分けて、.mdファイルで保存しています。

リモート会議などで、画面共有している内容をSnapshotして、画像を貼り付けながらメモできるのが便利です。

## 2. 報告文書作成
議事メモや会話メモをMarkdown形式でまとめているので、その内容をもとにGitHubCopilotで報告向け文章としてまとめさせています。

## 3. 簡単なスライド資料作成


## 公開
README.mdを書く。書かないと以下のエラーになる。
```
 ERROR  It seems the README.md still contains template text. Make sure t contains template text. Make sure to edit the README.md file before you package or publish your extension. 
```

https://code.visualstudio.com/api/working-with-extensions/publishing-extension#packaging-extensions

```bash
npm install -g @vscode/vsce
```

```bash
vsce package
```

weekly-report-0.0.1.vsix ファイルが作成される。


コマンドからVSCodeに拡張機能のVSIXファイルをインストールする。
```bash
code --install-extension my-extension-0.0.1.vsix
```

:::details 実行結果
```bash
PS C:\Users\nom40\Documents\vscode-extensions\weekly-report> code --install-extension .\weekly-report-0.0.1.vsix
Installing extensions...
Extension 'weekly-report-0.0.1.vsix' was successfully installed.
```
:::