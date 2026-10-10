# 解説イラストの生成

記事のQualityを上げるため、概念・アーキテクチャ・処理フローなど「絵で見せた方が伝わる箇所」には、Microsoft Foundry にデプロイ済みの画像生成モデルで解説画像を生成して挿入する。

:::message alert
**抽象的なメタファーだけの絵は「イメージ画像」で終わり、分かりにくいと判断される。** ロボットのキャラクターや虫眼鏡で書類を探す人といった雰囲気重視のイラストだけでは、記事の具体的な内容（用語・数値・判定結果）と結びつかず、読者にとって説明として機能しない。**単語ラベルを置くだけでも不十分。** 「Choice」とだけ書くのではなく「選択肢から1つを選ぶ」のように、要素が何をするかを説明する短いキャプション文まで画像内に入れる。`gpt-image-2.5-flare` は日本語の複合フレーズ（10文字程度）でも崩れずきれいに描画できるため、単語ラベルではなくキャプション文を書かせるのが分かりやすさの分岐点になる（後述の `labeled` スタイル）。雰囲気だけのメタファーが許されるのは、その画像単体で意味が完結する非常に単純な対比（例: 「喋るAI」と「喋らず即答するAI」）に限る。
:::

---

## 使う場面 / 使わない場面

| 使う | 使わない |
|------|---------|
| 概念説明・仕組みの図解（具体的な用語をラベルとして入れる） | 実際の操作画面（Azure Portal、VS Code等のスクリーンショット） |
| 実行結果・判定結果の視覚化（記事中の実データをラベル・数値として入れる） | コード自体（コードブロックで十分） |
| アーキテクチャ全体像・処理フロー（Mermaidで表現しにくい直感的な対比） | Mermaidで正確に表現できる構造図（役割が重複する） |

- 構造が明確なフロー図・アーキテクチャ図は Mermaid が適している場合も多い。**「正確な構造」は Mermaid、「具体的な内容を一目で分からせる図解」はイラスト**、と使い分ける。同じ内容を両方で説明しない。
- **記事中に既に登場する実データ（用語・数値・判定結果）を画像に持ち込む**のが分かりやすさの鍵。例えば実行結果の表がある場合、その表の内容をラベル・数値付きの図として視覚化すると、表の直後に置いても情報の重複ではなく「理解の補助」になる。
- 1記事あたり目安 1〜3枚程度。挿入しすぎると逆に読みにくくなるので、記事の要所（概念導入、主要な実行結果の直後）に絞る。
- 配置場所は「その画像が説明する具体的な内容が既にテキストで登場した直後」にする。抽象的な導入部より、実データが出そろった場所に置く方が分かりやすくなることが多い。

---

## 使用モデル

- Microsoft Foundry リソース: `ai-poc-eastus2-resource`（eastus2, リソースグループ `rg-ai-poc-eastus2`）
- デプロイ名: `gpt-image-2.5-flare`（画像生成・画像編集に対応）
- 別のモデルやリソースに切り替わっている可能性があるため、実行前に一度デプロイ状況を確認する:

```bash
az cognitiveservices account deployment list \
  --name ai-poc-eastus2-resource --resource-group rg-ai-poc-eastus2 -o table
```

`gpt-image-*` 系のデプロイ名が見つかればそれを使う（無ければユーザーに確認する）。見つかったデプロイ名が `gpt-image-2.5-flare` と異なる場合は、後述の環境変数 `AZURE_FOUNDRY_IMAGE_DEPLOYMENT` で上書きする。

---

## セットアップ（APIキーの取得）

Azure CLI にログイン済みであることが前提。

```bash
# bash
export AZURE_FOUNDRY_IMAGE_API_KEY=$(az cognitiveservices account keys list \
  --name ai-poc-eastus2-resource --resource-group rg-ai-poc-eastus2 \
  --query key1 -o tsv)
```

```powershell
# PowerShell
$env:AZURE_FOUNDRY_IMAGE_API_KEY = (az cognitiveservices account keys list `
  --name ai-poc-eastus2-resource --resource-group rg-ai-poc-eastus2 `
  --query key1 -o tsv)
```

エンドポイント・デプロイ名・APIバージョンが既定値と異なる場合のみ、以下も設定する（既定値は [generate_illustration.py](scripts/generate_illustration.py) 冒頭を参照）。

- `AZURE_FOUNDRY_IMAGE_ENDPOINT`
- `AZURE_FOUNDRY_IMAGE_DEPLOYMENT`
- `AZURE_FOUNDRY_IMAGE_API_VERSION`

APIキーは出力に含めない・ログに残さない・記事や Git にコミットしないこと。

---

## スクリプトの使い方

Python 3 + `requests` ライブラリが必要（`pip install requests` で導入済みでなければ事前にインストールする）。

```bash
python .claude/skills/zenn-tech-blog/scripts/generate_illustration.py \
  --style labeled \
  --subject "日本語ラベル付きの図解内容を具体的に指示する" \
  --output images/{slug}/overview.png
```

:::message alert
**Windows注意（重要）**: `--subject` に日本語を渡す場合、`PYTHONUTF8=1` を付けずに実行するとコンソールのデフォルトエンコーディングでコマンドライン引数が文字化けし、生成される文字も壊れる。**必ず先頭に `PYTHONUTF8=1` を付けて実行する**。

```bash
PYTHONUTF8=1 python .claude/skills/zenn-tech-blog/scripts/generate_illustration.py --style labeled --subject "..." --output ...
```
:::

主なオプション:

| オプション | 説明 | 既定値 |
|-----------|------|--------|
| `--subject` | 説明したい内容。ラベルを入れる場合はラベル文言そのものも含めて具体的に指示する | 必須 |
| `--output` | 保存先。記事の慣習に合わせ `images/{slug}/xxx.png` にする | 必須 |
| `--style` | 画風プリセット。`labeled`（ラベル・数値入りインフォグラフィック、**基本これを使う**）/ `sketch`（文字なし手描き風、単純な対比のみ）/ `flat`（文字なしフラットイラスト） | `sketch` |
| `--size` | `1024x1024` / `1024x1536` / `1536x1024` / `auto` | `1024x1024` |
| `--quality` | `low` / `medium` / `high` / `auto`。ラベル入りはテキストが崩れにくいよう `high` 推奨 | `medium` |
| `--n` | 生成枚数（バリエーションを比較したい時）。複数枚は `-1.png` のように連番保存される | `1` |
| `--raw-prompt` | スタイルプリセットを付与せず `--subject` をそのままプロンプトにする（プリセットにない細かい構図指定をしたい時） | off |
| `--input-image` | 既存画像の一部だけ直す（誤字の修正など）。`images/edits` を使い、`--subject` は編集指示になる（プリセットは付かない） | なし |
| `--subject-file` | `--subject` の代わりに、UTF-8のテキストファイルからプロンプトを読む。長文（記事全文など）を渡すときに使う | なし |

生成後は `images/{slug}/xxx.png` を記事本文に通常の画像記法で挿入する:

```markdown
![](/images/{slug}/overview.png)
```

---

## プロンプトのコツ（`labeled` スタイル / 文字入り解説図）

**テキスト精度は高い**。`gpt-image-2.5-flare` は英語・日本語（漢字・ひらがな混在）ともに、単語だけでなく **10文字程度の複合フレーズ**（例: 「選択肢から1つを選ぶ」「話題は近いが対象読者が違う」）まで崩れずくっきり生成できる。これを活かし、**要素名のラベルだけでなく、それが何をするか・何を意味するかを説明するキャプション文まで画像に書かせる**。

- `--subject` の中で、ラベルとキャプションをそれぞれ `'...'` で明示的に指定する（例: `title 'Choice'`, `caption below reading '選択肢から1つを選ぶ'`）
- **単語ラベルだけで終わらせない**。「Choice」の下に「選択肢から1つを選ぶ」のような一言説明を必ず添える
- 記事に既に出てきた具体的な要素（発行者名、スコア、判定結果、用語名など）とその意味をそのまま使う。抽象的な例え話に置き換えない
- 図の構造を先に決めてから文章にする: 「横棒グラフを3段、各行にラベル・数値・状態アイコン・説明キャプション」「しきい値の線で上下に分かれ、それぞれに数値バッジと説明文」など、レイアウトと各要素の内容を明示する
- 数値・記号（`✅` `❌` チェックマーク、パーセンテージ、色分けバー）とキャプション文を併用すると理解がさらに速くなる
- 難読漢字（「閾値」等）は崩れることがある。崩れた場合は `しきい値` のようにひらがな表記に変えて再生成すると安定する
- 生成結果は**必ず拡大して文字を目視確認する**。1文字でも違う漢字や崩れた文字があれば再生成する（1枚あたり低コストなので数回試すのが前提）

### 例（実績あり）

```
--style labeled --subject "A hand-drawn whiteboard explainer diagram, like a teacher's study note, \
three vertical sections side by side, each with a title label at top and a short descriptive Japanese \
caption phrase below the icon explaining what it does (not just a single word): first section title \
'Choice' with icon of a hand picking one highlighted card out of three colored option cards, caption \
below reading '選択肢から1つを選ぶ'; second section title 'Score' with icon of a horizontal gauge meter \
needle pointing to a middle level, caption below reading '段階で評価する'; third section title 'Noul' \
with icon of a Yes/No toggle switch with a badge '90%', caption below reading 'Yes・Noを確率で返す'."
```

もう一例、実データの表を視覚化するパターン（棒グラフ + 数値 + 判定 + 一言キャプション）:

```
--style labeled --subject "A hand-drawn whiteboard explainer diagram with a title at the top reading \
'類似度検索だけでは区別できない'. Three horizontal rows, each row has: a Japanese label on the left, a \
bar-chart bar showing a similarity score with the number printed at the end of the bar, a status icon \
on the right, and a short Japanese caption phrase explaining the judgement below the bar. Row 1: label \
'デジタル庁', long green bar with number '0.81', green checkmark icon, caption '対象読者が一致（正解）'. \
Row 2: label '総務省・経産省', medium orange bar with number '0.65', yellow warning triangle icon, caption \
'話題は近いが対象読者が違う'. Row 3: label '観光庁', short gray bar with number '0.23', red X icon, caption \
'そもそも無関係'."
```

## プロンプトのコツ（`sketch` / `flat` スタイル / 文字なしメタファー）

単純な二項対立（例: 「長文を書くAI」vs「即答するAI」）のように、文字がなくても一目で伝わる場合のみ使う。

- 主語を明確にする: 「何と何がどう関係しているか」を1文で書く
- 登場要素は絞る（3〜5個程度）。詰め込みすぎると絵が煩雑になる
- プリセットに `no text, no letters, no words` を含めているので、`--raw-prompt` を使う場合も踏襲する

## 既存画像の誤字を直す

ユーザーが貼った画像や生成済みの画像に誤字があるときは、作り直さず `--input-image` で編集する。

- `--subject` に「変えるのは○か所だけ、他は同一」と明記し、現在の誤った文言と直したあとの文言の両方を書く
- 語を消したいときも、消したあとの文言をそのまま書く（例: 「LLM（Jev）に」を「Jevに」に）
- `--size auto --quality high` にすると、元の縦横比のまま出力される（1072x636 の元画像で確認）
- 出力は元画像とは別のパスに書き、全体を目視で確認してから上書きする

## 記事の冒頭サムネイルを作る

記事の内容がひと目で伝わる冒頭画像は、記事全文をそのままプロンプトに渡して生成する（約2万文字の記事で問題なく生成できた）。

1. サムネイル用の指示文、記事全文、念押しの1行を、1つのテキストファイルにまとめる。プロンプトの上限は約32,000文字なので、記事が長すぎる場合はコードブロックなどを削る
2. 指示文には「タイトルを2行で大きく、指示文に書いた文字列のとおりに」「要素は3〜4個、ラベルは10文字以内」「記事にない情報を作らない」「手描きホワイトボード風、パステル、白背景」を入れる
3. `--subject-file プロンプトファイル --raw-prompt --size 1536x1024 --quality high --n 2` で2案を出す
4. タイトルの文字が正確か、記事にない要素が混ざっていないか、記事の主題と矛盾する描写がないか（例: 「文章を生成しない」のに吹き出しで喋っている）を見て、1案を選ぶ
5. frontmatter の直後に `![](/images/{slug}/thumbnail.png)` として入れる

Windowsでは、Pythonのコード内にGit Bash形式のパス（`/c/...`）を書くとファイルが見つからない。`C:/...` の形式で書く。
