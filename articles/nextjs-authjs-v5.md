---
title: "Next.js と Auth.js でWebアプリにGoogleアカウント認証と認可を実装しよう"
emoji: "🧑‍🤝‍🧑"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["nextjs", "authjs", "azure", "cosmosdb", "google"]
published: false
---

# はじめに
個人的に開発しているアプリに、困ったときになんでも答えてくれるナレッジ管理とチャットアプリがあります。
![](/images/nextjs-authjs-v5/2025-05-10-15-36-26.png)

例えば、我が家が停電したときに何をしたらいいか？　いざというときに教えてほしいですよね。
![](/images/nextjs-authjs-v5/2025-05-10-15-35-05.png)

他にも住んでいる市のごみ捨てルールを知りたかったり。
![](/images/nextjs-authjs-v5/2025-05-10-15-39-36.png)

今回は、このようなNext.jsで作られたアプリケーションに、Googleアカウント認証と認可を実装していきます。
実装のご参考になれば幸いです。

# Auth.js とは
https://authjs.dev/
Auth.jsは、Webアプリケーションの認証機能を簡単に実装できるオープンソースのライブラリです。 以前は「NextAuth.js」と呼ばれていましたが、バージョン5へのアップデートに伴い「Auth.js」という名称に変更されました。

このライブラリを使うことで、GoogleやGitHubなどの外部サービスを利用したログイン機能を簡単に追加できます。 また、セッション管理やJWT（JSON Web Token）を活用した認証もサポートしています。

- ✅ 複数の認証方式をサポート OAuth（Google, GitHub, Twitterなど）、メール認証、パスワード認証、WebAuthn（パスキー）など、さまざまな認証方法を利用できます。
- ✅ セッション管理が簡単 JWTやデータベースを利用したセッション管理が可能で、ログイン状態の維持や自動更新を簡単に実装できます。
- ✅ Next.jsとの相性が抜群 Next.jsのApp Routerと統合しやすく、APIルートを使った認証フローを構築できます。


# 実装
まずはGoogleアカウント認証を実装し、そのあと認可を実装していきます。

前提：
- Next.jsのプロジェクトが作成されていること
- Azure Cosmos DBが作成されていること

### Auth.js v5のインストール
まずはNext.jsのプロジェクトにAuth.jsをインストールします。
```bash
npm install next-auth@beta
```

### AUTH_SECRET 環境変数
Auth.jsを使用するためには、AUTH_SECRET環境変数を設定します。
```bash
npx auth secret
```

![](/images/nextjs-authjs-v5/2025-05-03-09-21-25.png)

.env.localに、AUTH_SECRETが追加されているはずです。

### Googleプロバイダ追加
Googleアカウント認証を実装するために、Googleプロバイダを追加します。

#### プロジェクト作成
Google Cloud Consoleにアクセスし、プロジェクトを作成します。
![](/images/nextjs-authjs-v5/2025-05-03-09-48-23.png)

#### OAuth認証画面の作成
![](/images/nextjs-authjs-v5/2025-05-03-09-48-10.png)

画面の指示に従って、OAuth認証画面を作成します。
![](/images/nextjs-authjs-v5/2025-05-03-09-49-47.png)

![](/images/nextjs-authjs-v5/2025-05-03-09-50-55.png)

![](/images/nextjs-authjs-v5/2025-05-03-09-51-13.png)

![](/images/nextjs-authjs-v5/2025-05-03-09-51-27.png)

#### OAuth クライアントの作成
作成したOAuth認証画面を選択して、OAuth クライアントを作成します。
![](/images/nextjs-authjs-v5/2025-05-03-09-52-30.png)

まずはローカル開発環境で稼働確認するため、JavaScript生成元とリダイレクトURIはlocalhostに設定します。
![](/images/nextjs-authjs-v5/2025-05-03-09-53-34.png)

クライアントIDとクライアントシークレットが表示されるので控えてしておきます。


#### 環境変数の追加
Google Cloud で、クライアントIDとクライアントシークレットが表示されます。
![](/images/nextjs-authjs-v5/2025-05-03-10-04-20.png)

この情報を、以下のように.env.localに追加します。
```bash
AUTH_GOOGLE_ID="クライアントID"
AUTH_GOOGLE_SECRET="クライアントシークレット"
```


## 実装
それでは、実際にAuth.jsを使ってGoogleアカウント認証と認可を実装していきます。

---
### Auth.jsの認証実装

#### auth.ts の実装

アプリケーションのルートディレクトリに、auth.tsを実装します。
auth.tsは、Auth.jsの設定をまとめるファイルで、主に以下の内容を定義できます。
- 認証プロバイダーの設定
- サインイン・サインアウトの処理
- セッション管理
- カスタム認証ロジック
- APIルートとの連携
```typescript
import NextAuth from "next-auth"
 
export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    providers: [Google],   //Googleプロバイダを設定
    trustHost: true,
    callbacks: {
      async signIn({ user }) {   // サインイン時の処理
        console.log("サインインしたアカウントのメールアドレス:", user.email);
      },
      async jwt({ token, user, account }) {   // JWTトークンの処理
        if (user && account?.id_token) {
          token.idToken = account?.id_token;
        }
        return token;
      },
      async session({ token, session }) {   // セッションの処理
        session.idToken = token.idToken;
        return session;
      },
    },
  ],
})
```

:::details 実装の解説
jwt（JSON Web Token）は、ユーザの認証情報や権限を含むデータを安全にやり取りするための仕組みです。
- token: JWTのオブジェクト。これにカスタムデータを追加できます。
- user: 認証されたユーザー情報。
- account: 認証プロバイダー（Googleなど）の情報。

処理の流れ
1. ✅ ユーザーが認証された場合、account.id_tokenを取得
2. ✅ tokenオブジェクトにidTokenとして保存 
3. ✅ return token; でJWTを更新し、次回以降のリクエストで使用可能にする
:::

#### ./app/api/auth/[...nextauth]/route.ts の実装
これは、認証APIのエンドポイントを定義するためのものです。 ./auth.tsで認証の設定を行い、それをAPIルートで使用できるようにするためにhandlersをエクスポートしています。
Next.jsのAppRouterを使っているので、app/配下に作成します。page Routerの場合は、page/api/auth/[...nextauth]/route.tsに作成します。
```typescript
import { handlers } from "@/auth";

export const { GET, POST } = handlers;
```

#### ./middleware.ts の実装
呼び出されるたびにセッションの有効期限を更新するための実装です。
```typescript
export { auth as middleware } from "./auth"
```

---
### アプリ接続時にサインインを求める実装
サインインしていない状態でアプリにアクセスした場合に、自動で以下のようにサインインを求める画面が表示されるようにします。
![](/images/nextjs-authjs-v5/2025-05-10-15-45-45.png)

app/layout.tsxに、以下を追加実装します。
- useEffectで、セッションを確認します。
- セッションがない場合は、signIn()を呼び出してサインインを促します。
- 認可ガードを適用して、サインインしていない場合は、アプリのコンテンツを表示しないようにします。
- サインインしている場合は、アプリのコンテンツを表示します。
```typescript
"use client";

import { Inter } from "next/font/google";
import "./globals.css";
import { SessionProvider, useSession, signIn } from "next-auth/react";
import { useEffect } from "react";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  useEffect(() => {
    const checkSession = async () => {
      const session = await fetch("/api/auth/session").then((res) => res.json());
      if (!session?.user) {
        signIn();
      }
    };
    checkSession();
  }, []);

  return (
    <html lang="ja">
      <body className={inter.className}>
        <SessionProvider>
          <AuthGuard>{children}</AuthGuard> {/* 認可ガードを適用 */}
        </SessionProvider>
      </body>
    </html>
  );
}

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return <div>読み込み中...</div>;
  }

  if (!session?.user) {
    return <div>ログインが必要です。</div>;
  }

  return <>{children}</>;
}
```



ここまでの実装で、アプリへの**アカウント認証**はできるようになりました。
アプリの接続時にサインインを求める画面が表示されます。
![](/images/nextjs-authjs-v5/2025-05-10-15-59-18.png)

そしてGoogleアカウントでサインインします。
![](/images/nextjs-authjs-v5/2025-05-10-16-01-32.png)

サインインできるとアプリにリダイレクトされます。


### 認可の実装
今のままでは、Googleアカウントを持っている人であれば誰でもアプリにアクセスできてしまいます。
認可を実装して、特定のGoogleアカウントを持っている人だけがアプリにアクセスできるようにします。

アプリへのアクセスを許可するGoogleアカウントのメールアドレスは、Azure Cosmos DBで管理します。
簡易的に実装するのであれば、環境変数などでも良いでしょう。
![](/images/nextjs-authjs-v5/2025-05-10-16-09-54.png)

![](/images/nextjs-authjs-v5/2025-05-10-16-24-33.png)

#### CosmosDB からメールアドレスを取得する実装

Azure Cosmos DBからメールアドレスを取得するための実装です。
```typescript
import { CosmosClient } from "@azure/cosmos";
import { AccountItem } from "../../models/models";
import dotenv from "dotenv";
dotenv.config();
/**
 * categoryを全取得する
 * @returns - カテゴリの配列
 * */
export const getAllAccounts = async (): Promise<AccountItem[]> => {
  return new Promise(async (resolve, reject) => {
    const cosmosClient = new CosmosClient(process.env.COSMOS_CONNECTION_STRING!);
    const database = cosmosClient.database(process.env.COSMOS_DATABASE_NAME!);
    const container = database.container(process.env.COSMOS_ACCOUNT_CONTAINER_NAME!);

    try {
      const { resources } = await container.items.readAll<AccountItem>().fetchAll();
      resolve(resources);
    } catch (error) {
      console.error("🚀Error retrieving accounts:", error);
      reject(error);
    }
  });
};
```

#### 認可ガードの実装
認可ガードを実装して、特定のGoogleアカウントを持っている人だけがアプリにアクセスできるようにします。
./auth.tsに、以下のように認可ガードを実装します。
```typescript
import type { NextAuthConfig } from "next-auth";
import Google from "next-auth/providers/google";
+ import { getAllAccounts } from "./src/util/cosmos/account";

+ let allowedEmails: string[] = [];

+ /**
+  * 許可されたメールアドレスを取得する関数
+ * @returns {Promise<string[]>} - 許可されたメールアドレスの配列
+ */
+async function fetchAllowedEmails() {
+  try {
+    allowedEmails = await getAllAccounts()
+      .then((accounts) => accounts.map((account) => account.email))
+    console.log("🚀Allowed emails updated:", allowedEmails);
+  } catch (error) {
+    console.error("Error fetching allowed emails:", error);
+  }
+}

+// 初期化時に許可されたメールアドレスを取得
+fetchAllowedEmails();

export const authConfig: NextAuthConfig = {
  providers: [Google],
  trustHost: true, // 型エラーを修正: trustHost を true に設定
  callbacks: {
+    async signIn({ user }) {
+      if (allowedEmails.includes(user.email || "")) {
+        console.log("許可されたメールアドレス:", user.email);
+        return true; // 許可されたメールアドレスの場合ログインを許可
+      }
+      console.log("許可されていないメールアドレス:", user.email);
+      return false; // 許可されていない場合ログインを拒否
+    },
    async jwt({ token, user, account }) {
      if (user && account?.id_token) {
        token.idToken = account?.id_token;
      }
      return token;
    },
    async session({ token, session }) {
      session.idToken = token.idToken;
      return session;
    },
  },
};
```

この実装により、許可されていないGooglaアカウントでサインインされた場合、以下のように認可エラーとなりアプリへのアクセスを拒否します。
![](/images/nextjs-authjs-v5/2025-05-10-16-28-50.png)

# まとめ
Next.js + Auth.jsを使って、Googleアカウント認証と認可を実装する方法について解説しました。
Auth.jsは、認証機能を簡単に実装できるライブラリで、GoogleやGitHubなどの外部サービスを利用したログイン機能を追加できます。 また、セッション管理やJWTを活用した認証もサポートしています。
認可を実装することで、特定のGoogleアカウントを持っている人だけがアプリにアクセスできるようにしました。

実装が参考になれば幸いです。