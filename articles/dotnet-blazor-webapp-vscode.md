---
title: "dotnetのBlazorフレームワークを用いたチャットアプリケーション（VSCode）"
emoji: "🐻‍❄️"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["dotnet", "Blazor", "CSharp", "VSCode"]
published: true
---

# dotnetのBlazorフレームワークを用いたチャットアプリケーション（VSCode）

## 背景
- dotnet（C#）でのWebアプリケーション開発を行うために、Blazorフレームワークを利用してみたい初学者人たちの記事です。
- streamlitなど、Pythonで簡単にWebアプリケーションを作成できるフレームワークがあります。しかし、**MicrosoftのSemanticKernelなどはC#を主にして開発されているため、C#でのWebアプリケーション開発をしておくと恩恵を受ける場面が多いと思います。**

## Blazorフレームワーク
- Blazorフレームワークは、C#でWebアプリケーションを開発するためのフレームワークです。
- 以下公式ページにチュートリアルはありますが、VisualStudio前提で記載されていますので、VSCodeでの開発を行うための手順を記載します。
    [公式ページリンク](https://dotnet.microsoft.com/ja-jp/learn/aspnet/blazor-tutorial/install)

## 前提
- VSCode利用
- DevContainerを使ったコンテナ開発

## 始めてみよう
以下公式ページの目次の赤枠の部分をVSCodeで実施します。
![公式ページ目次](/images/dotnet-blazor-webapp-vscode/2024-01-06-19-55-16.png)

1. 開発用コンテナを作成する
   - .devcontainerフォルダを作成し、以下の内容でdevcontainer.jsonを作成
       ```json
       {
           "name": "C# (.NET)",
           "image": "mcr.microsoft.com/devcontainers/dotnet:1-8.0-bookworm",

           "customizations": {
               "vscode": {
                   "extensions": [
                       "ms-azuretools.vscode-docker",
                   ]
               }
           }
       }
       ```
   - コマンドパレットから「Reopen in Container」を選択

2. Visual Studio Code のターミナルを開く
   - 以下コマンドを実行し、Blazorアプリケーションのテンプレートを作成する。
        ※プロジェクト名を指定すると、新規ディレクトリが作成されます。ここではカレントディレクトリに直接配置したいため、プロジェクト名は指定しません。
       ```bash
       dotnet new blazorwasm
       ```
       ![blazorテンプレート作成](/images/dotnet-blazor-webapp-vscode/2024-01-06-19-18-29.png)
    - このディレクトリ構成になります。
        ![blazorテンプレート作成](/images/dotnet-blazor-webapp-vscode/2024-01-06-19-26-08.png)

3. 作成されたプロジェクトを実行して動作確認
   - 以下コマンドを実行し、プロジェクトを実行します。
       ```bash
       dotnet run
       ```
       ![実行](/images/dotnet-blazor-webapp-vscode/2024-01-06-19-48-06.png)
   - ブラウザで上記赤枠に表示されるURLにアクセスします。
      以下のように表示されれば成功です。
      ![初期画面表示確認](/images/dotnet-blazor-webapp-vscode/2024-01-06-19-49-15.png)

残りのチュートリアルは、公式ページの通りに進めていけばOKです。
[公式ページ](https://dotnet.microsoft.com/ja-jp/learn/aspnet/blazor-tutorial/try) 
       
## まとめ
これで、VSCodeでBlazorフレームワークを使ったWebアプリケーション開発ができるようになります。
次は、Microsoftから提供されるチャットベースのアプリケーションがあるのでそちらを生かす方法を紹介します。