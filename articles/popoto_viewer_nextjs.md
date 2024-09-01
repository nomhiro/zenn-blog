---
title: ""
emoji: "🌟"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

# 検証環境
- windows11
- Docker環境

# Neo4jを用意
https://neo4j.com/licensing/

エディションは３つ
- Neo4j Community Editionは
  - 完全にオープンソースで、GPL v3の下でライセンス供与および配布
  - 個人でも会社でも、Neo4jデータベースにアクセスするアプリを自由に開発できる
- Neo4j Enterprise Edition
  - スケールと可用性が重要な商用デプロイメント向けに設計されている。
  - ３つのライセンスオプションがある。
    - Neo4j Commercial License（商用ライセンス）
      - Neo4j、Inc.による商用支援が含まれる。
    - Neo4j Development License（開発ライセンス）
      - 登録は無料で、Enterprise Editionの無料開発ライセンスが含まれており、ローカルデスクトップでNeo4j Enterpriseを使用してアプリケーションを開発できる。
    - Neo4j Evaluation License（評価ライセンス）
      - Enterprise Editionの評価を希望するユーザーが使う。
      - Enterprise Edition の全機能が提供される。
      - Neo4jの専門家による支援も含まれる。
- Neo4j AuraDB
  - クラウドでNeo4jを実行する方法。
  - マネージドなサブスクリプションベース
  - データベースの日常的な管理をNeo4jを作ったエンジニアに任せることができ、アプリケーションの構築に集中できる

この記事ではCommunity Editionのコンテナイメージを使います！
- debian 11 community　タグ
- OSはdebian 11です。

## Neo4jをコンテナで起動
https://neo4j.com/docs/operations-manual/current/docker/introduction/

docker-compose.ymlを定義します。
環境変数にneo4jのアカウント情報を設定しています。アカウント名/パスワードの形式です。
指定しないとデフォルトでneo4j/neo4jになります。以下のように指定する場合は、パスワードにneo4j以外を指定しないとneo4j起動時にエラーになります。
```yml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.23.0-bullseye
    container_name: neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/neo4j0825
    volumes:
      - ./data:/data
      - ./logs:/logs
      - ./import:/import
      - ./plugins:/plugins
```

コンテナを起動します。
```bash
docker-compose up -d
```

コンテナの状態がStartedになり、
![](/images/popoto_viewer_nextjs/2024-08-25-18-25-49.png)

neo4jコンテナのログが以下のようになれば起動完了です。
![](/images/popoto_viewer_nextjs/2024-08-25-18-29-20.png)

neo4jブラウザにアクセスします。
http://localhost:7474/

docker-composeで設定したUsernameとPasswordを入力して接続
![](/images/popoto_viewer_nextjs/2024-08-25-20-26-56.png)

接続できました。このneo4jブラウザを使い、neo4jに格納したデータをビジュアル的に確認できます。
![](/images/popoto_viewer_nextjs/2024-08-25-20-27-57.png)

## Neo4jにサンプルデータを登録

以下の小説の登場人物の関係性をNeo4jに登録してみます。
:::details 小説

水川朱紀

ふと目線をあげると景色がゆらゆらと揺れている。ああ陽炎が立っている。恨めしくなるほど快晴な夏空の中、伊吹は隣の男を見やる。この暑さの中汗ひとつかかず、むしろ寒さで震えているとばかりに真っ青なのは、伊吹の相棒である志摩。やっぱりまだ早かったのではないかと内心苦さを感じる。
8月9日、かつての相棒である香坂の墓参り。勤務中からどこか上の空な志摩を問い詰め続け墓参りに行くことを白状させ付き添いをほぼ無理やり了承させたのは伊吹である。
お寺が見えてきた。何度か帰らせようと説得するも「大丈夫」としか言わないマシーンと化した志摩の顔色に慄いた住職が寺へ招き入れてくれた。
「桶とか水とか色々いるでしょ、取ってくるから志摩ちゃん座ってて！」
お茶をもってきた住職に志摩を預けて、少し先の石階段へ向かって駆け出した。

石階段を駆け上がる途中、反対側から人が降りてくる。抜けるような青空と紺色のワンピース、白い日傘のコントラストが眩しい。すれ違う瞬間ふわりと漂った香りに思わず振り向いた。どれとも表現し難い、ただ目を閉じて感じたくなるような香りがした。


季節外れの台風も珍しくなくなった近年、だんだんと雨足が強くなる外を見ながらコンビニの店員は「今日は早く帰りたい」とぼやいていた。
そこへ客が1人入ってくる。もっていたのはおそらくこの強風で使い物にならなくなった折りたたみ傘。帽子を被ったその人は雨合羽を買った。会計をしながらなんとなくこの人はどこにも帰らないのではという予感がした。
そうして

大事なことにはいつも間に合わない
例えば受験の日、熱を出して志望校は諦めた
例えば母の最期の瞬間、そばにいられなかった
そして彼のSOSにも気づけず喪った

それでもこれだけは「正義の味方」に届けなくてはいけない、間に合わなくてはいけない
震える手で受話器を取る。コール音はほどなくして途切れた
「もしもし」
心なしか不機嫌な低音があの気難しいそうな顔を思い起こさせて場違いにも笑いそうになってしまった。
「誰だ」
そんなこちらの気配を読んだのか一段声が下がる。気持ちを切り替える。
「刈谷さん」
声でわかったのだろうか、「無事か」「ちゃんと飯食ってるか」
内容は刑事というより心配性な父親のそれで結局笑ってしまった

「あんた今どこにいる」
きっとこの人はわたしが今どこにいても探そうとするだろう、でも今はダメだ
「町田公園入り口から東に30メートルの公衆電話、そこに置いていきます。ちゃんと見つけてくれないと困りますよ。」
素人のわたしはこれ以上これを守りながら逃げ切れる自信がないのだ。
刈谷さん、後はお願いしますね。
おい、待て、どういう
ガシャンと受話器を置く。今はこれしか方法がない。刈谷さんはきっと来てくれる。あの人ならこの微々たるものでも真相を見つけ出してくれるはず。私にできるのはせいぜい少しの時間稼ぎくらいだろう。
だからまだ捕まるわけにはいかない。

話は最後まで聞け！！！！！
虚しく響く切断音に思わず怒鳴ったのは仕方がないことだと思う。何回言ったところで、止めたところで聞きやしない。せめてあいつが残したものを確実に手にするしか手掛かりがない。十中八九あいつの母親の話も絡んでくる。
相棒の田島にどこまで隠し通せるか。あいつは聡い、きっと俺の態度に不審に思うだろう。だが今回は気づかれればすべてが終わる。まだ若い、こんなところで潰すわけにはいかない。
外はバケツをひっくり返したような雨が降っている。初めて対面したあの日のように。

「警察は正義を掲げているはずでしょう。なのにどうしてですか。彼の憧れた正義は何だったんですか。」
そう問いただすずぶ濡れのあいつの頬に流れるのは雨か涙か

警察官として、刑事として、誇りをもってやってきた。たとえどんな理不尽なことがあろうと。だが投げられた言葉に返すことができなかった。
「あんたは相棒のことをどう思ってる？」
ゆっくりと顔を上げた女は綺麗に笑っていた。
「どう思っていてほしいですか？」

何年経って思い出すからどうしてくれよう。相変わらずひどい雨だ。まもなく嵐がくる。


2週間前？
「暑いーーーーー」
「うるせえ！！余計に暑いわ！！！」
「志摩ちゃん怒鳴るとさらに暑いからほんとやめて」
今月に入ってから分駐所のエアコンの調子が悪く効き目がすごぶるよくない。昨今の猛暑には致命的である。暑さにのびる伊吹を見ながら「犬がのびてる」と考える志摩に「なんか今志摩ちゃんがシツレーなこと考えてる気がする」と野生の勘を発揮する伊吹、何かとうるさい2人にいつものようにツッコむ元気もない陣馬、ここ最近のよくある光景である。
「お疲れさまです。あ、たしかにぬるいですね」
そう言って爽やかに入ってきたのは警察庁に戻り日々研鑽を積む九重、元相棒の陣馬を今でも心のから尊敬し慕っている。
「三浦署の帰りにアイスクリーム店があったので、どうぞ食べてください。」
「九ちゃん天使なの？？？」「九重さん神かよ」「ありがとなーー九重」
「どういたしまして。そこの2人、自分は人間です」
やいのやいの言いながら涼しい恵みに舌鼓を打つ。食べ終わる頃、「そういえば」と九重が思い出したように声をかけた。
「さっき志摩さんを訪ねてきた女性を見かけたのですが」
「え、なに署まで会いにきてくれる彼女いたの！？俺聞いてないんだけど！？」
「お袋さんとかじゃないのか？」陣馬も横から問いかける。
「いねえわ、地味に心を抉るな！家族が来るとは聞いてないですね。」
「20代後半から30歳前後の女性でした。『4機捜の志摩一未さん』って言っていたので面識があるのかと。でも案内される前に電話をしながら慌てて外に出ていかれました。」
「どんな人だったの？」
「綺麗な方でしたよ。160㎝前半の痩せ型、黒髪ロング、服は…」
警察官らしく外見的な特徴的を挙げていく中、最後の言葉が志摩の動きを止めた。
「左目尻に泣きぼくろが3つ並んでいました」
結構珍しい特徴ですよねと朗らかな会話が続く中、志摩の耳には聞こえなくなった。
特徴が合致する人物は知る限り1人だけ　あの日幸せそうに笑っていた、あの日必死に涙を堪えていたその人だけ　
どこからかウイスキーの香りがした



「志摩どうしたの？顔色めちゃくちゃ悪いよ」
思わず手を伸ばした伊吹の手を志摩は払いのけた。
「なんでもない」
「いや、なんでもないわけないじゃん」
『至急至急、西武蔵野署管内で傷害事件発生。男性が血を流して倒れているとの通報。現場に急行せよ』
無線連絡がほとんど終わると同時に副隊長の谷山が入ってくる。
「まただぞ、被害者はIT系の経営者、現場の話じゃ同じ万年筆が落ちていたようだ。」
谷山が「また」というのはここ1ヶ月で発生しているIT関連の企業経営者を狙った連続傷害事件である。そして必ず同じメーカーの万年筆が残されていた。3件も続けば、犯人からの何かしらのメッセージと考えてもいいと判断されている。
「陣馬さんたちは現場の応援に、志摩と伊吹は西武蔵野署に桔梗さんを迎えに行ってくれ」
「え、なんで隊長？」
「今は署長だ。陣頭指揮は桔梗さんがとることになった。上と話があるようだから迎えが必要だ。」
「やったじゃん、志摩ちゃん」
「うるせえ、はっ倒すぞ」「え、こっわ」
いつものような軽快なやりとりとともに、志摩の顔色もさっきのあの血色の悪さが嘘のように戻っている。
泣きぼくろが3つ並んだ綺麗な女性、志摩の知っている人なのか、また何かあるのか。伊吹はのちに振り返る。あのときちゃんと聞いておけばよかった、のちに後悔することになった。
:::

上記の小説からAOAIでCypherクエリを生成させてみます。
システムメッセージはこちら。
:::txt
あなたはNeo4jにデータ登録するためにCypherクエリを生成する役割です。
ユーザメッセージで与えられた小説の登場人物の関係性をGraphで表現するCypherクエリを生成してください。
:::

生成されたCypherクエリは以下の通りです。
```cypher
// 登場人物のノードを作成  
CREATE (mizukawa:Person {name: '水川朱紀'})  
CREATE (ibuki:Person {name: '伊吹'})  
CREATE (shima:Person {name: '志摩'})  
CREATE (kosaka:Person {name: '香坂'})  
CREATE (priest:Person {name: '住職'})  
CREATE (kariya:Person {name: '刈谷'})  
CREATE (tajima:Person {name: '田島'})  
CREATE (kujyuu:Person {name: '九重'})  
CREATE (jimba:Person {name: '陣馬'})  
CREATE (taniyama:Person {name: '谷山'})  
CREATE (kikyou:Person {name: '桔梗'})  
CREATE (convenience_store_clerk:Person {name: 'コンビニの店員'})  
CREATE (customer:Person {name: '客'})  
CREATE (mysterious_woman:Person {name: '謎の女性'})  
CREATE (deceased_mother:Person {name: '亡くなった母'})  
CREATE (injured_man:Person {name: '負傷した男性'})  
  
// 関係性のエッジを作成  
CREATE (ibuki)-[:PARTNER]->(shima)  
CREATE (shima)-[:PARTNER]->(ibuki)  
CREATE (ibuki)-[:VISITING_GRAVE_OF]->(kosaka)  
CREATE (shima)-[:VISITING_GRAVE_OF]->(kosaka)  
CREATE (shima)-[:QUESTIONED_BY]->(ibuki)  
CREATE (priest)-[:INVITED_IN]->(shima)  
CREATE (priest)-[:INVITED_IN]->(ibuki)  
CREATE (convenience_store_clerk)-[:SERVED]->(customer)  
CREATE (kariya)-[:RECEIVED_CALL_FROM]->(mysterious_woman)  
CREATE (kariya)-[:PARTNER]->(tajima)  
CREATE (tajima)-[:PARTNER]->(kariya)  
CREATE (shima)-[:VISITED_BY]->(mysterious_woman)  
CREATE (kariya)-[:INVESTIGATING]->(injured_man)  
CREATE (tajima)-[:INVESTIGATING]->(injured_man)  
CREATE (ibuki)-[:WORKS_WITH]->(jimba)  
CREATE (shima)-[:WORKS_WITH]->(jimba)  
CREATE (jimba)-[:MENTORED]->(kujyuu)  
CREATE (kujyuu)-[:RESPECTS]->(jimba)  
CREATE (taniyama)-[:GIVES_ORDERS_TO]->(shima)  
CREATE (taniyama)-[:GIVES_ORDERS_TO]->(ibuki)  
CREATE (taniyama)-[:ASSIGNS_TASK_TO]->(jimba)  
CREATE (kikyou)-[:COMMANDS]->(shima)  
CREATE (kikyou)-[:COMMANDS]->(ibuki)  
CREATE (kariya)-[:RECEIVES_ITEM_FROM]->(mysterious_woman)  
CREATE (mysterious_woman)-[:REMEMBERS]->(deceased_mother)  
CREATE (shima)-[:REMINISCES_ABOUT]->(deceased_mother)  
```

PythonコードでNeo4jにデータを登録します。
:::details Pythonコード
```python
from neo4j import GraphDatabase

# Neo4jにデータを登録するためのスクリプト
# 接続先：neo4j://neo4j:neo4j0825@localhost:7687/db/data

# Connect to Neo4j
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "neo4j0825"

driver = GraphDatabase.driver(uri, auth=(username, password))

# Create a session
with driver.session() as session:
  # すべてのデータを削除する
  print("🚀 Deleting all data")
  session.run("MATCH (n) DETACH DELETE n")
  
  # データを登録する
  print("🚀 Create data")
  # Personノードを追加
  persons = ['水川朱紀', '伊吹', '志摩', '香坂', '住職', '刈谷', '田島', '九重', '陣馬', '谷山', '桔梗', 'コンビニの店員', '客', '謎の女性', '亡くなった母', '負傷した男性']
  for person in persons:
    session.run(f'''
    CREATE (:Person {{ name: "{person}" }})
    ''')

  # 関係性を追加
  relationships = [
    ('伊吹', '志摩', 'PARTNER'),
    ('志摩', '伊吹', 'PARTNER'),
    ('伊吹', '香坂', 'VISITING_GRAVE_OF'),
    ('志摩', '香坂', 'VISITING_GRAVE_OF'),
    ('志摩', '伊吹', 'QUESTIONED_BY'),
    ('住職', '志摩', 'INVITED_IN'),
    ('住職', '伊吹', 'INVITED_IN'),
    ('コンビニの店員', '客', 'SERVED'),
    ('刈谷', '謎の女性', 'RECEIVED_CALL_FROM'),
    ('刈谷', '田島', 'PARTNER'),
    ('田島', '刈谷', 'PARTNER'),
    ('志摩', '謎の女性', 'VISITED_BY'),
    ('刈谷', '負傷した男性', 'INVESTIGATING'),
    ('田島', '負傷した男性', 'INVESTIGATING'),
    ('伊吹', '陣馬', 'WORKS_WITH'),
    ('志摩', '陣馬', 'WORKS_WITH'),
    ('陣馬', '九重', 'MENTORED'),
    ('九重', '陣馬', 'RESPECTS'),
    ('谷山', '志摩', 'GIVES_ORDERS_TO'),
    ('谷山', '伊吹', 'GIVES_ORDERS_TO'),
    ('谷山', '陣馬', 'ASSIGNS_TASK_TO'),
    ('桔梗', '志摩', 'COMMANDS'),
    ('桔梗', '伊吹', 'COMMANDS'),
    ('刈谷', '謎の女性', 'RECEIVES_ITEM_FROM'),
    ('謎の女性', '亡くなった母', 'REMEMBERS'),
    ('志摩', '亡くなった母', 'REMINISCES_ABOUT')
  ]

  for relationship in relationships:
    session.run(f'''
    MATCH (a:Person {{name: "{relationship[0]}"}}), (b:Person {{name: "{relationship[1]}"}})
    MERGE (a)-[:{relationship[2]}]->(b)
    ''')

# Close the driver
driver.close()
```
:::

Neo4jブラウザ（http://localhost:7474/browser/）でクエリを実行し、登録したGraphデータを取得します。
```cypher
MATCH (n)-[r]-(p) RETURN n,r,p
```

![](/images/popoto_viewer_nextjs/2024-08-27-19-19-13.png)

登録されました。
![](/images/popoto_viewer_nextjs/2024-08-27-19-25-41.png)

次に、Next.jsでNeo4jに登録したデータを取得し、グラフを表示します。

# Next.jsでNeo4jのデータを表示したい

## Next.jsのプロジェクトを作成

Next.jsのプロジェクトを作成します。
```bash
npx create-next-app popoto_viewer_nextjs
```

Success! となればOK！
![](/images/popoto_viewer_nextjs/2024-08-27-20-37-26.png)

念のため稼働確認
```bash
cd popoto_viewer_nextjs
npm run dev
```

http://localhost:3000/ にアクセスして、Next.jsのデフォルトページが表示されればOKです。
![](/images/popoto_viewer_nextjs/2024-08-27-20-49-28.png)

## グラフをViewするための実装

package.jsonにpopotoパッケージを追加します。
```json
"@types/popoto": "^3.0.4",
"popoto": "^4.0.6"
```

npm installしてパッケージをインストールします。
```bash
npm install
```

