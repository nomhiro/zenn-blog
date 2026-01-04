---
title: "AndroidゲームをUnityで作るチュートリアル ~ AIサポートのおかげ~"
emoji: "🐡"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["Unity", "Android", "ゲーム開発", "生成AI", "AI"]
published: false
---

![](/images/android-game-create-unity-tutorial/2026-01-04-14-16-29.png)

# はじめに
知人と飲み会をしたときに、Unityの話になり、そういえば触れたことがないなぁと思い、くそげーとも言えないレベルのチュートリアルAndroidゲームを作ってみることにしました。
※3時間ほどあれば作れます。

というのも、昨今の生成AIに進化のおかげで、自分の知らない領域のことでも、AIと対話しながら学びながらモノづくりできてしまいます。ハードルがかなり下がったなと実感しました。

:::message alert
**Unityの学習をメイン**にしているため、AIに依頼するのは実装ではなく学習資料と題材ゲーム作成の手順のみとしています。

ちなみに、Unityのゲーム開発をAI駆動開発するのは、限界がありそうです。
- ×：UnityEditorでしか設定できない設定値は、手動となる。
- 〇：スクリプトコードの生成は得意分野なので、AIに任せられる。
現状では**AIに任せられることと手動でやることの切り分けが必要**です。
:::

# AIとともにハンズオン内容と学習資料を作成する

ひとまず、AIに聞いてみましょう。

```
Windows環境で、Unityで簡単なAndroidゲームを作って、Unityの勉強をしたいです。
学ぶべきことを洗い出し、題材を決めて学習資料を作成してください。

---
最新のUnity情報を調べてください。
```

これである程度の情報があつまります。ただ学ぶだけではなく、題材となる簡単なゲームがあるといいですよね。追加で依頼しましょう。


```
Unityならではの物理演算やスマホの加速度センサーを使うようなゲームを作成する題材を考えてほしいです。。わたしは初心者なので、解説を含んだ詳細な手順書を作成してください。手順書はMarkdownファイルで。
```

さて、これである程度の手順書が出来上がります。さて、早速始めていきましょう。


## 必要なスペックと前提条件

このブログで紹介するUnityを使用したAndroidゲーム開発チュートリアルでは、以下のシステム要件とアカウントを前提としています。

- **OS**: Windows 11 (64bit)
- **CPU**: AMD Ryzen AI 9 365 w/ Radeon 880M (2.00 GHz)
- **RAM**: 32.0 GB

### 必要なアカウント

1. **Unity アカウント**（無料）: https://id.unity.com/
2. **GitHub アカウント**（無料）: https://github.com/
3. **Google アカウント**（Android開発者登録用、25ドル一回限り）

**合計初期費用**: 25ドル（Google Play登録のみ）+ 月額0〜50ドル

---

# Unity Hub & Unity Editor のインストール

### Step 1: Unity Hub のダウンロードとインストール

1. **Unity Hub 公式サイト**にアクセス: https://unity.com/download
2. 「Download Unity Hub」ボタンをクリック
3. ダウンロードしたインストーラーを実行
   - Windows: `UnityHubSetup.exe`
   - macOS: `UnityHub.dmg`
4. インストールウィザードに従い、デフォルト設定でインストール
5. Unity Hub を起動

### Step 2: Unity アカウントでサインイン

1. Unity Hub 右上の「Sign in」をクリック
2. Unity ID でログイン（アカウントがない場合は「Create account」から作成）
3. Unity Personal ライセンスを選択（無料）

### Step 3: Unity Editor のインストール（重要：Android Build Support を含む）

1. Unity Hub の左メニューから「Installs」タブを選択
2. 右上の「Install Editor」ボタンをクリック
  ![](/images/android-game-create-unity-tutorial/2025-10-18-13-11-36.png)
3. **推奨バージョンを選択**:
   - **Unity 2022 LTS** (2022.3.x) - 安定版、推奨
   - または **Unity 6 LTS** (6000.0.x) - 最新機能を試したい場合
   ![](/images/android-game-create-unity-tutorial/2025-10-18-13-12-26.png)
4. 「Continue」をクリック
5. **必須モジュールを選択**（これが最重要！）:
   - ✅ **Android Build Support** をチェック
     - その下の **Android SDK & NDK Tools** をチェック
     - その下の **OpenJDK** をチェック
   - ✅ **Microsoft Visual Studio Community 2022** (Windows)
     - または **Visual Studio for Mac** (macOS)
   - その他のモジュールは不要（後で追加可能）
   ![](/images/android-game-create-unity-tutorial/2025-10-18-13-13-37.png)
6. 「Continue」→ ライセンス同意 → 「Done」
7. ダウンロードとインストールが開始（5〜15GB、20〜60分かかる）

**インストール完了の確認**:
- Unity Hub の「Installs」タブに Unity 2022.3.x が表示されればOK

---

# Unity 3D 玉転がしゲーム 作成チュートリアル

こんな感じのゲームを作ります！
https://youtu.be/5Kb64DtMjpI?si=5uc3ueKgURBqcJqH

## 📁 プロジェクトの作成

### 新規プロジェクト作成

- Unity Hub を起動して、左側の「プロジェクト」タブをクリック
- 右上の「新しいプロジェクト」ボタンをクリック
- テンプレート選択画面で以下を設定

| 設定項目 | 設定値 |
| -------- | ------ |
| テンプレート3D | (Built-in Render Pipeline) |
| プロジェクト名| RollABall |
| 保存場所| 任意の場所（日本語パスは避ける） |

![](/images/android-game-create-unity-tutorial/2026-01-04-09-22-01.png)

### Input System の確認
Unity 6 では Input System がデフォルトで有効になっています。
念のため確認しておきましょう。

- Edit → Project Settings を開く
- 左メニューから「Player」を選択
- 「Other Settings」セクションを展開
- 「Active Input Handling」が以下のいずれかになっていることを確認：
  - Input System Package (New) ← 推奨
  - Both ← これでもOK

![](/images/android-game-create-unity-tutorial/2026-01-04-11-06-41.png)

:::message
💡 Input System とは？
Unity の新しい入力システムです。キーボード、マウス、ゲームパッド、タッチ、
加速度センサーなど、あらゆる入力を統一的に扱えます。
:::

### TextMeshPro の初期設定
初回のみ、TextMeshPro の Essential Resources をインポートします。

- Window → TextMeshPro → Import TMP Essential Resources
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-11-10-03.png)
- Import ダイアログが表示されたら「Import」をクリック
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-11-10-29.png)

:::message
💡 TextMeshPro とは？
高品質なテキスト描画システムです。Legacy Text より美しく、多機能です。
Unity 6 では標準的なテキスト表示方法として推奨されています。
:::

### フォルダ構成の準備
Project ウィンドウで整理用フォルダを作成します。

- Assets フォルダ内で右クリック → Create → Folder
- 以下のフォルダを作成
  - Scripts （スクリプト用）
  - Materials （マテリアル用）
  - Prefabs （プレハブ用）

![](/images/android-game-create-unity-tutorial/2026-01-04-09-26-00.png)

## 🎮 Input Actions の設定

新しい Input System では、入力設定を Input Actions アセットで管理します。

### Input Actions アセットの作成

- Project の Input フォルダ内で右クリック
- Create → Input Actions
- 名前を「PlayerInputActions」に変更
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-11-19-59.png)
- ダブルクリックして Input Actions Editor を開く

### Action Map の作成

- 左側の「Action Maps」の「+」をクリック
- 名前を「Player」に変更

![](/images/android-game-create-unity-tutorial/2026-01-04-11-22-43.png)

### Move アクションの作成

- 中央の「Actions」の「+」をクリック
- 名前を「Move」に変更
- Action Type を「Value」に変更
- Control Type を「Vector2」に変更

![](/images/android-game-create-unity-tutorial/2026-01-04-11-22-36.png)

### キーボード入力のバインド

- Move アクションの「+」をクリック → Add Up/Down/Left/Right Composite
- 名前を「WASD」に変更
- 各方向をクリックして Path を設定：

| 方向 | Pathの設定手順 |
|------|----------------|
| Up | Keyboard → W |
| Down | Keyboard → S |
| Left | Keyboard → A |
| Right | Keyboard → D |

![](/images/android-game-create-unity-tutorial/2026-01-04-11-24-37.png)

- 同様に矢印キーも追加：
  - Move の「+」→ Add Up/Down/Left/Right Composite
  - 名前を「Arrows」に変更
  - Up: Up Arrow, Down: Down Arrow, Left: Left Arrow, Right: Right Arrow

![](/images/android-game-create-unity-tutorial/2026-01-04-11-25-40.png)

### 設定を保存

- ウィンドウ上部の「Save Asset」をクリック
- Inspector で PlayerInputActions を選択
- 「Generate C# Class」にチェックを入れる
- 「Apply」をクリック

これで PlayerInputActions.cs が自動生成されます。

:::message
💡 Input Actions の利点
- 入力デバイスを意識せずにコードを書ける
- ボタン配置の変更がエディターだけで可能
- 複数デバイス（キーボード、ゲームパッド、センサー）を統一的に扱える
:::

## ステージ（床）を作る

### 床の作成

- Hierarchy で右クリック → 3D Object → Plane
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-09-30-35.png)
- 名前を「Ground」に変更（F2キー）
- Inspector で以下を設定：

| Component | 項目 | 設定値 |
|-----------|------|--------|
| Transform | Position | X: 0, Y: 0, Z: 0 |
| Transform | Rotation | X: 0, Y: 0, Z: 0 |
| Transform | Scale | X: 2, Y: 1, Z: 2 |

:::message 
💡 **Plane のサイズについて**
Plane は標準で 10×10 ユニットの大きさです。
Scale を 2 にすると 20×20 ユニットのステージになります。
:::

![](/images/android-game-create-unity-tutorial/2026-01-04-09-31-47.png)

### 床のマテリアル（色）を作成
見た目をわかりやすくするため、床に色をつけます。

- Project の Materials フォルダ内で右クリック
- Create → Material
- 名前を「GroundMaterial」に変更
- Inspector で以下を設定：

| 項目 | 設定値 |
|------|--------|
| Albedo（色）| 好きな色（例：濃い緑 #2E7D32） |

![](/images/android-game-create-unity-tutorial/2026-01-04-09-33-57.png)

![](/images/android-game-create-unity-tutorial/2026-01-04-09-34-10.png)

- GroundMaterial を Hierarchy の Ground にドラッグ＆ドロップ

:::message
💡 **マテリアルとは？**
オブジェクトの見た目（色、質感、反射など）を定義するものです。
同じマテリアルを複数のオブジェクトに適用できます。
:::

![](/images/android-game-create-unity-tutorial/2026-01-04-09-35-40.png)

## 🧱 Step 3: 壁を作る
ボールがステージから落ちないよう、四方に壁を作ります。

### 壁の作成（1つ目）

- Hierarchy で右クリック → 3D Object → Cube
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-09-36-11.png)
- 名前を「WallNorth」に変更
- Inspector で以下を設定：

| 項目 | 設定値 | 説明 |
|------|--------|------|
| Position | X: 0, Y: 0.5, Z: 10 | ステージの奥側に配置 |
| Scale | X: 20.5, Y: 1, Z: 0.5 | 横長の壁に調整 |

![](/images/android-game-create-unity-tutorial/2026-01-04-09-39-47.png)

### 壁のマテリアル作成

- Materials フォルダに新規マテリアル「WallMaterial」を作成
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-09-41-31.png)
- Albedo を好きな色に（例：グレー #9E9E9E）
- WallNorth に適用

![](/images/android-game-create-unity-tutorial/2026-01-04-09-41-54.png)

### 残り3つの壁を作成

- WallNorth を複製（Ctrl+D）して、位置を変更：

| 名前 | Position | Scale |
|------|----------|-------|
| WallSouth | X: 0, Y: 0.5, Z: -10 | X: 20.5, Y: 1, Z: 0.5 |
| WallEast | X: 10, Y: 0.5, Z: 0 | X: 0.5, Y: 1, Z: 20.5 |
| WallWest | X: -10, Y: 0.5, Z: 0 | X: 0.5, Y: 1, Z: 20.5 |

![](/images/android-game-create-unity-tutorial/2026-01-04-09-43-50.png)

### 壁を整理

- Hierarchy で右クリック → Create Empty
- 名前を「Walls」に変更
- Position を (0, 0, 0) に設定
- 4つの壁を Walls の子にドラッグ

![](/images/android-game-create-unity-tutorial/2026-01-04-09-52-49.png)

## ⚽ Step 4: プレイヤー（ボール）を作る

### ボールの作成

- Hierarchy で右クリック → 3D Object → Sphere
- 名前を「Player」に変更
- Inspector で以下を設定

| Component | 項目 | 設定値 |
|-----------|------|--------|
| Transform | Position | X: 0, Y: 0.5, Z: 0 |
| Transform | Scale | X: 1, Y: 1, Z: 1 |

![](/images/android-game-create-unity-tutorial/2026-01-04-10-05-15.png)

### ボールのマテリアル作成

- Materials フォルダに「PlayerMaterial」を作成
- Albedo を目立つ色に（例：青 #2196F3）
- Player に適用

![](/images/android-game-create-unity-tutorial/2026-01-04-10-24-33.png)

### Rigidbody（物理演算）の追加
ボールが物理法則に従って動くようにします。

- Player を選択
- Inspector で「Add Component」をクリック
- 検索欄に「Rigidbody」と入力して追加（2Dではない方）

:::message
⚠️ 注意: 「Rigidbody」を選択してください。「Rigidbody 2D」ではありません。
:::

- Rigidbody コンポーネントの設定

| 項目 | 設定値 | 説明 |
|------|--------|------|
| Mass | 1 | ボールの質量 |
| Linear Damping | 0.5 | 空気抵抗（転がりを滑らかに） |
| Angular Damping | 0.5 | 回転の抵抗 |
| Use Gravity | ✓（チェック） | 重力の影響を受ける |
| Collision Detection | Continuous | 高速でもすり抜けない |

![](/images/android-game-create-unity-tutorial/2026-01-04-10-29-15.png)

:::message
💡 Rigidbody とは？
オブジェクトに物理演算を適用するコンポーネントです。
これを追加するだけで、重力で落下したり、他のオブジェクトと衝突したりします。
https://docs.unity3d.com/6000.2/Documentation/Manual/class-Rigidbody.html
:::

### Player Input コンポーネントの追加

Player Input コンポーネントを追加して、Input Actions と接続します。

- Player を選択
- Add Component → Player Input
- Actions に PlayerInputActions をドラッグ＆ドロップ
- Default Map が「Player」になっていることを確認
- Behavior を「Invoke Unity Events」に変更

![](/images/android-game-create-unity-tutorial/2026-01-04-11-47-22.png)

:::message
💡 Player Input コンポーネント
Input Actions と GameObject を接続するコンポーネントです。
これにより、設定した入力アクションがこのオブジェクトで使えるようになります。
:::

### 動作確認

- ▶ ボタンでPlayモード開始
  - ボールが床の上に静止していることを確認
  - Scene ビューでボールを選択し、上に移動させると落下することを確認
- ▶ を再度クリックして停止

## 🎮 ボール操作スクリプト
傾きセンサーとキーボードでボールを操作するスクリプトを作成します。

### スクリプトの作成

- Project の Scripts フォルダ内で右クリック
- Create → C# Script
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-10-37-34.png)
- 名前を「PlayerController」に変更
- ダブルクリックしてエディターで開く（私の場合はVisual Studio Codeです
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-10-39-46.png)

### スクリプトのコード
以下のコードを入力（既存の内容は全て置き換え）

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

/// <summary>
/// プレイヤー（ボール）の操作を制御するスクリプト
/// Unity 6 の Input System を使用
/// </summary>
public class PlayerController : MonoBehaviour
{
    [Header("移動設定")]
    [Tooltip("ボールに加える力の強さ")]
    [SerializeField] private float moveForce = 10f;
    
    [Tooltip("最大速度")]
    [SerializeField] private float maxSpeed = 10f;

    [Header("傾き設定")]
    [Tooltip("傾きセンサーの感度")]
    [SerializeField] private float tiltSensitivity = 2.0f;

    private Rigidbody rb;
    private Vector2 moveInput;
    private bool useAccelerometer = false;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        
        if (rb == null)
        {
            Debug.LogError("Rigidbodyコンポーネントが見つかりません！");
            return;
        }

        // 加速度センサーを有効化（モバイル用）
        EnableAccelerometerIfAvailable();
    }

    void Update()
    {
        // 加速度センサーが有効な場合、毎フレーム値を読み取る
        if (useAccelerometer && Accelerometer.current != null)
        {
            Vector3 accel = Accelerometer.current.acceleration.ReadValue();
            
            // 加速度センサーの値を移動入力に変換
            // X: 左右の傾き、Y: 前後の傾き
            moveInput = new Vector2(accel.x * tiltSensitivity, accel.y * tiltSensitivity);
        }
    }

    void FixedUpdate()
    {
        MovePlayer();
    }

    /// <summary>
    /// Move アクションのイベントハンドラ
    /// Player Input コンポーネントから呼び出される（キーボード/ゲームパッド用）
    /// </summary>
    public void OnMove(InputAction.CallbackContext context)
    {
        // キーボード/ゲームパッドの入力がある場合は加速度センサーより優先
        Vector2 input = context.ReadValue<Vector2>();
        
        if (input.magnitude > 0.1f)
        {
            moveInput = input;
            // 入力がある間は加速度センサーを一時的に無視
        }
    }

    void MovePlayer()
    {
        if (rb == null) return;

        // 2D入力を3D方向に変換
        Vector3 movement = new Vector3(moveInput.x, 0f, moveInput.y);

        if (movement.magnitude > 1f)
        {
            movement.Normalize();
        }

        // 最大速度未満なら力を加える
        if (rb.linearVelocity.magnitude < maxSpeed)
        {
            rb.AddForce(movement * moveForce, ForceMode.Force);
        }
    }

    void EnableAccelerometerIfAvailable()
    {
        if (Accelerometer.current != null)
        {
            InputSystem.EnableDevice(Accelerometer.current);
            useAccelerometer = true;
            Debug.Log("加速度センサーを有効化しました");
        }
        else
        {
            useAccelerometer = false;
            Debug.Log("加速度センサーは利用できません");
        }
    }

    /// <summary>
    /// ボールをリセットする
    /// </summary>
    public void ResetPlayer(Vector3 position)
    {
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        transform.position = position;
    }
}
```

- ファイルを保存（Ctrl+S）
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-10-40-13.png)

### スクリプトをアタッチ

- Unityエディターに戻る
- Hierarchy で Player を選択
- Project の Scripts フォルダから PlayerController を Inspector にドラッグ＆ドロップ

![](/images/android-game-create-unity-tutorial/2026-01-04-10-42-02.png)

### Player Input のイベント接続

Player Input コンポーネントの Move イベントを PlayerController の OnMove メソッドに接続します。

- Player を選択
- Inspector の Player Input コンポーネントを展開
- Events → Player を展開
- Move イベントの「+」をクリック
- Player オブジェクト自身をドラッグ＆ドロップ
- ドロップダウンから PlayerController → OnMove を選択

### 動作テスト

▶ ボタンでPlayモード開始
矢印キーまたはWASDキーでボールが動くことを確認
壁にぶつかると止まることを確認
▶ を再度クリックして停止

:::message
💡 Input System のイベント駆動
旧方式（Update で毎フレーム Input.GetAxis をチェック）と違い、
Input System はイベント駆動で動作します。
入力があった時だけ OnMove が呼ばれるため、効率的です。
:::

## 📷 Step 7: カメラの設定

### カメラ追従スクリプト

Scripts フォルダに「CameraController」を作成

```csharp
using UnityEngine;

/// <summary>
/// カメラがプレイヤーを追従するスクリプト
/// </summary>
public class CameraController : MonoBehaviour
{
    [Header("追従設定")]
    [SerializeField] private Transform target;
    [SerializeField] private float smoothSpeed = 5f;

    private Vector3 offset;

    void Start()
    {
        if (target != null)
        {
            offset = transform.position - target.position;
        }
    }

    void LateUpdate()
    {
        if (target == null) return;

        Vector3 desiredPosition = target.position + offset;
        Vector3 smoothedPosition = Vector3.Lerp(
            transform.position,
            desiredPosition,
            smoothSpeed * Time.deltaTime
        );
        transform.position = smoothedPosition;
    }
}
```

![](/images/android-game-create-unity-tutorial/2026-01-04-11-56-36.png)

### カメラの設定

- Main Camera を選択
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-01-09.png)
- 位置と角度を設定

| 項目 | 設定値 |
|------|--------|
| Position | X: 0, Y: 10, Z: -10 |
| Rotation | X: 45, Y: 0, Z: 0 |

![](/images/android-game-create-unity-tutorial/2026-01-04-12-02-09.png)

- CameraController をアタッチ
- Target に Player をドラッグ＆ドロップ

### 動作テスト

▶ ボタンでPlayモード開始
ボールを操作するとカメラが追従することを確認
▶ を再度クリックして停止

## 💎 収集アイテムを作る

### アイテムの作成

- Hierarchy で右クリック → 3D Object → Cube
- 名前を「PickupItem」に変更

| 項目 | 設定値 |
|------|--------|
| Position | X: 3, Y: 0.5, Z: 3 |
| Rotation | X: 45, Y: 45, Z: 45 |
| Scale | X: 0.5, Y: 0.5, Z: 0.5 |

### アイテムのマテリアル

- Materials フォルダに「PickupMaterial」を作成
- Albedo: 黄色（#FFEB3B）
- Emission にチェック、色を黄色に
- PickupItem に適用

![](/images/android-game-create-unity-tutorial/2026-01-04-12-09-55.png)

:::message
💡 Emission とは？
オブジェクトが自ら光を放つ効果を追加します。
暗い場所でも目立つようになります。
:::

### アイテム回転スクリプト

Scripts フォルダに「PickupRotator」を作成

```csharp
using UnityEngine;

/// <summary>
/// アイテムを回転させる
/// </summary>
public class PickupRotator : MonoBehaviour
{
    [SerializeField] private Vector3 rotationSpeed = new Vector3(15f, 30f, 45f);

    void Update()
    {
        transform.Rotate(rotationSpeed * Time.deltaTime);
    }
}
```

![](/images/android-game-create-unity-tutorial/2026-01-04-12-09-21.png)

PickupItem にアタッチ

![](/images/android-game-create-unity-tutorial/2026-01-04-12-10-27.png)

### 当たり判定の設定

PickupItem の Box Collider で「Is Trigger」にチェック

![](/images/android-game-create-unity-tutorial/2026-01-04-12-11-12.png)

:::message
💡 Is Trigger とは？
チェックすると物理的な衝突はせず、すり抜けながら接触を検知できます。
:::

### ゲームマネージャースクリプト

Scripts フォルダに「GameManager」を作成

```csharp
using UnityEngine;
using UnityEngine.SceneManagement;
using TMPro;

/// <summary>
/// ゲーム全体の進行を管理
/// </summary>
public class GameManager : MonoBehaviour
{
    [Header("UI参照")]
    [SerializeField] private TextMeshProUGUI scoreText;
    [SerializeField] private TextMeshProUGUI itemCountText;
    [SerializeField] private GameObject gameClearPanel;
    [SerializeField] private GameObject gameOverPanel;

    [Header("ゲーム設定")]
    [Tooltip("落下判定のY座標")]
    [SerializeField] private float fallThreshold = -5f;

    private int score = 0;
    private int totalItems;
    private int collectedItems = 0;
    private PlayerController player;
    private bool isGameOver = false;

    void Start()
    {
        InitializeGame();
    }

    void Update()
    {
        if (!isGameOver)
        {
            CheckFall();
        }
    }

    void InitializeGame()
    {
        player = FindFirstObjectByType<PlayerController>();
        totalItems = FindObjectsByType<PickupItem>(FindObjectsSortMode.None).Length;

        UpdateUI();

        if (gameClearPanel != null) gameClearPanel.SetActive(false);
        if (gameOverPanel != null) gameOverPanel.SetActive(false);

        Time.timeScale = 1f;
    }

    public void AddScore(int points)
    {
        score += points;
        UpdateUI();
    }

    public void ItemCollected()
    {
        collectedItems++;
        UpdateUI();

        if (collectedItems >= totalItems)
        {
            GameClear();
        }
    }

    public void RestartGame()
    {
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }

    void CheckFall()
    {
        if (player != null && player.transform.position.y < fallThreshold)
        {
            GameOver();
        }
    }

    void GameClear()
    {
        isGameOver = true;
        if (gameClearPanel != null)
        {
            gameClearPanel.SetActive(true);
        }
        Time.timeScale = 0f;
    }

    void GameOver()
    {
        isGameOver = true;
        if (gameOverPanel != null)
        {
            gameOverPanel.SetActive(true);
        }
        Time.timeScale = 0f;
    }

    void UpdateUI()
    {
        if (scoreText != null)
        {
            scoreText.text = $"Score: {score}";
        }
        if (itemCountText != null)
        {
            itemCountText.text = $"Items: {collectedItems}/{totalItems}";
        }
    }
}
```

![](/images/android-game-create-unity-tutorial/2026-01-04-12-24-34.png)

### アイテム取得スクリプト
Scripts フォルダに「PickupItem」を作成

```csharp
using UnityEngine;

/// <summary>
/// 収集アイテム
/// </summary>
public class PickupItem : MonoBehaviour
{
    [SerializeField] private int scoreValue = 10;

    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            GameManager gameManager = FindFirstObjectByType<GameManager>();
            if (gameManager != null)
            {
                gameManager.AddScore(scoreValue);
                gameManager.ItemCollected();
            }
            Destroy(gameObject);
        }
    }
}
```

![](/images/android-game-create-unity-tutorial/2026-01-04-12-12-57.png)

PickupItem オブジェクトにアタッチ

![](/images/android-game-create-unity-tutorial/2026-01-04-12-25-52.png)

### Prefab化

- Hierarchy の PickupItem を Project の Prefabs フォルダにドラッグ
- ダイアログで「Original Prefab」を選択

:::message
💡 Prefab とは？
オブジェクトの雛形です。Prefab にすることで、同じ設定のオブジェクトを簡単に複製できます。
:::

### アイテムを複数配置

- Prefabs フォルダの PickupItem を Hierarchy にドラッグして複数配置

| 番号 | Position |
|------|----------|
| 1 | X: 3, Y: 0.5, Z: 3 |
| 2 | X: -3, Y: 0.5, Z: 3 |
| 3 | X: 3, Y: 0.5, Z: -3 |
| 4 | X: -3, Y: 0.5, Z: -3 |
| 5 | X: 0, Y: 0.5, Z: 5 |
| 6 | X: 5, Y: 0.5, Z: 0 |
| 7 | X: -5, Y: 0.5, Z: 0 |
| 8 | X: 0, Y: 0.5, Z: -5 |

- Create Empty で「Pickups」を作成
- 全ての PickupItem を子にまとめる

![](/images/android-game-create-unity-tutorial/2026-01-04-12-34-14.png)

## 🎯 GameManager をセットアップ

### GameManager オブジェクトの作成

- Hierarchy で右クリック → Create Empty
- 名前を「GameManager」に変更
- GameManager スクリプトをアタッチ

※📝 UI の設定は Step 10 で行うため、Inspector の参照欄は後で設定します。

![](/images/android-game-create-unity-tutorial/2026-01-04-12-35-28.png)

## 📊 UI を作る（TextMeshPro）

### Canvas の作成

- Hierarchy で右クリック → UI → Canvas
- Canvas を選択し、Canvas Scaler を設定：

| 項目 | 設定値 |
|------|--------|
| UI Scale Mode | Scale With Screen Size |
| Reference Resolution | X: 1080, Y: 1920 |
| Match | 0.5 |

![](/images/android-game-create-unity-tutorial/2026-01-04-12-39-53.png)

### スコアテキスト

- Canvas を右クリック → UI → Text - TextMeshPro
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-40-44.png)
- 初回は「Import TMP Essentials」ダイアログが出たら Import をクリック
- 名前を「ScoreText」に変更
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-40-55.png)
- Rect Transform 設定
  - Anchor: 左上（Anchor Presets で Alt+Shift を押しながら左上をクリック）
  - Pos X: 30, Pos Y: -30
  - Width: 300, Height: 60
- TextMeshPro - Text (UI) コンポーネント設定：
  - Text: Score: 0
  - Font Size: 40
  - Vertex Color: 白

![](/images/android-game-create-unity-tutorial/2026-01-04-12-43-33.png)

### アイテムカウントテキスト

- ScoreText を複製（Ctrl+D）
- 名前を「ItemCountText」に変更
- Pos Y: -100
- Text: Items: 0/0

![](/images/android-game-create-unity-tutorial/2026-01-04-12-43-45.png)

### 操作説明テキスト

- Canvas を右クリック → UI → Text - TextMeshPro
- 名前「InstructionText」
- Anchor: 下中央
- Pos X: 0, Pos Y: 50
- Width: 600, Height: 50
- Text: Tilt to move / Arrow keys on PC
- Font Size: 28
- Alignment: Center（中央揃え）

### ゲームクリアパネル

- Canvas を右クリック → UI → Panel
- 名前を「GameClearPanel」に変更
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-51-52.png)
- Image コンポーネントの Color: 半透明の緑 (R:0, G:150, B:0, A:200)
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-52-47.png)
- GameClearPanel を右クリック → UI → Text - TextMeshPro
  - Text: CLEAR!
  - Font Size: 100
  - Alignment: Center
  - Vertex Color: 白
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-55-02.png)
- GameClearPanel を右クリック → UI → Button - TextMeshPro
  - 名前「RetryButton」
  - 子の Text を「RETRY」に変更
  - Font Size: 36
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-12-54-41.png)

### Retry ボタンのイベント設定

- RetryButton を選択
- Inspector の On Click() セクションで「+」をクリック
- Hierarchy の GameManager をドラッグ＆ドロップ
- ドロップダウンから GameManager → RestartGame を選択

![](/images/android-game-create-unity-tutorial/2026-01-04-12-55-50.png)

### ゲームオーバーパネル

- GameClearPanel を複製（Ctrl+D）
- 名前を「GameOverPanel」に変更
- Image Color: 半透明の赤 (R:150, G:0, B:0, A:200)
- 子のテキストを GAME OVER に変更

### GameManager に UI を接続

- Hierarchy で GameManager を選択
- Inspector で各項目にドラッグ＆ドロップ：

| 項目 | 接続するオブジェクト |
|------|----------------------|
| Score Text | ScoreText |
| Item Count Text | ItemCountText |
| Game Clear Panel | GameClearPanel |
| Game Over Panel | GameOverPanel |

### 動作テスト

▶ ボタンでPlayモード開始
ボールを操作してアイテムを取得し、スコアとアイテム数が更新されることを確認
全アイテム取得でクリアパネルが表示されることを確認
ボールを落としてゲームオーバーパネルが表示されることを確認
▶ を再度クリックして停止

## 🕳️ 落下エリアを作る（難易度調整）

壁の一部に穴を開けて、落下するとゲームオーバーになるようにします。

### 壁に穴を開ける

- Walls → WallNorth を選択
- Scale X を 8 に変更（短くする）
- Position X を -6 に変更（左寄せ）
- WallNorth を複製（Ctrl+D）
- 複製した方の Position X を 6 に変更（右寄せ）

これで北側の壁の中央に穴ができ、落ちるとゲームオーバーになります。

![](/images/android-game-create-unity-tutorial/2026-01-04-13-09-35.png)

## 📱Android ビルド

### シーン保存

- File → Save As... をクリック
- 保存場所は Assets → Scenes フォルダを選択
- ファイル名を「GameScene」と入力
- 「保存」をクリック

### Build Profiles を開く

- File → Build Profiles を選択（または Ctrl+Shift+B）
- Build Profiles ウィンドウが開く

:::message
💡 Build Profiles とは？
Unity 6 の新機能で、複数のビルド設定を保存・管理できます。
旧バージョンの「Build Settings」に代わるものです。
:::

### Android ビルドプロファイルの作成

- Build Profiles ウィンドウの左下にある「Add Build Profile」をクリック
- Platform Browser ウィンドウが開く
- Android を選択
- 「Add Build Profile」をクリック

![](/images/android-game-create-unity-tutorial/2026-01-04-13-29-06.png)

### プラットフォームの切り替え

- 作成した Android プロファイルを選択
- 右上の「Switch Profile」をクリック
- 切り替え処理を待つ（初回は数分かかります）

### シーンの追加

- Build Profiles ウィンドウの「Scene List」セクションを確認
- シーンがない場合は「Add Open Scenes」をクリック
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-13-30-05.png)
- GameScene が追加されていることを確認
  - ![](/images/android-game-create-unity-tutorial/2026-01-04-13-30-15.png)

### Player Settings の設定

- Build Profiles ウィンドウ内の「Player Settings」セクションを展開
- または Edit → Project Settings → Player を開く

以下の項目を設定

| 項目 | 設定値 |
|------|--------|
| Company Name | YourName（半角英数） |
| Product Name | RollABall |

Other Settings セクションを展開
Identification で以下を設定

| 項目 | 設定値 | 説明 |
|------|--------|------|
| Package Name | com.yourname.rollaball | アプリの一意識別子 |
| Version | 1.0 | アプリバージョン |
| Minimum API Level | Android 6.0 (API level 23) | 対応最低バージョン |
| Target API Level | Automatic (highest installed) | 推奨 |

:::message
⚠️ Package Name の形式
com.会社名.アプリ名 の形式で、半角英数字と.のみ使用可能。
例: com.nomu.rollaball
:::

Resolution and Presentation

- Resolution and Presentation セクションを展開
- Orientation で以下を設定

| 項目 | 設定値 | 説明 |
|------|--------|------|
| Default Orientation | Landscape Left | 横向き（推奨） |

### ビルド実行

- Build Profiles ウィンドウに戻る
- 「Build」ボタンをクリック
- 保存場所を選択し、ファイル名を RollABall.apk と入力
- 「保存」をクリック
- ビルド完了を待つ

:::message
💡 Build And Run
Android 端末を USB 接続している場合、「Build And Run」を選択すると
ビルド後に自動でインストール・起動されます。

1. Android 端末で「開発者向けオプション」を有効にする
   1. 設定 → デバイス情報（または「端末情報」）
   2. 「ビルド番号」を 7回タップ
   3. 「開発者になりました」と表示される
2. USB デバッグを有効にする
   1. 設定 → システム → 開発者向けオプション
   2. 「USB デバッグ」を ON にする
3. USB 接続モードを確認
   1. USB ケーブルで PC と接続
   2. 端末に「USB の使用」ダイアログが表示されたら「ファイル転送」を選択
   3. 「USB デバッグを許可しますか？」と表示されたら「許可」をタップ
:::

### 実機テスト

- APK ファイルを Android 端末にコピー
- 端末の設定で「提供元不明のアプリ」を許可
- ファイルマネージャーで APK をタップしてインストール
- ゲームを起動
- スマホを傾けて操作できることを確認！

