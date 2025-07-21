---
title: "AMD Ryzen AI NPUでMicrosoft Phi-4を動作させる技術調査レポート"
emoji: "🐈"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["AI", "NPU", "phi4", "AMD", "ONNX"]
published: false
---

# はじめに
以前のこちらのブログでは、Foundry Local を使い、SLM（phi-4など）をCPUやGPUがある環境で利用する方法を書きました。
https://zenn.dev/nomhiro/articles/slm-foundry-local-poc-01

今回は、AMD Ryzen™ AI 9 365 10コア/20 スレッド・プロセッサー（最大 50 NPU TOPS）で SLM を動かして、どのくらいのパフォーマンスの差があるのか確認してみます。

# Microsoft Phi-4 最新仕様とリリース情報

**Microsoft Phi-4**は2024年12月12日に正式リリースされた最新の小規模言語モデルです。**14Bパラメータ**を持つDense decoder-only Transformerアーキテクチャを採用し、**16Kトークン**のInputコンテキストを入れられます。

- パラメータ数：14B（14億パラメータ）
- アーキテクチャ：40層、40アテンションヘッド
- 埋め込み次元：5120
- 語彙サイズ：100,352トークン
- 訓練データ：9.8T tokens

# AMD Ryzen AI NPUでSLMを動作させるには？

**ONNX Runtime with DirectML**を使います。DirectX 12ベースのハードウェア加速により、広範なハードウェア互換性を提供します。現在のAMD Ryzen AI 300シリーズでは、NPU+iGPUを協調させる**ハイブリッド実行モード**が利用可能です。

**Vitis AI Execution Provider**は、NPU専用実行による低電力・高効率な推論を提供します。INT8/BF16量子化をサポートし、モバイル用途に最適化されています。

## ONNX変換と開発環境構築の具体的手順

### システム要件と事前準備

**必要環境**：
- Windows 11 (build >= 22621.3527)
- Visual Studio 2022 Community
- 16GB以上のRAM
- 50GB以上の空き容量

### NPUドライバーのインストール

こちらからダウンロードしてインストールします。
https://ryzenai.docs.amd.com/en/latest/inst.html

※前提
- Windows11 : build 22621.3527 以降
  - 「C++ を使用したデスクトップ開発」がインストールされていること
- Visual Studio : 2022
- cmake : 3.26 以降
    https://cmake.org/download/#latest
- Miniforge
    https://conda-forge.org/download/
    以下の3つの環境変数PATHに以下の値を設定しておきます。
    ・path\to\miniforge3\condabin
    ・path\to\miniforge3\Scripts
    ・path\to\miniforge3\
  - Python : latest version


RyzenAIソフトウェアインストーラーをダウンロードします。
https://account.amd.com/en/forms/downloads/ryzen-ai-software-platform-xef.html?filename=ryzen-ai-1.5.0.msi

MSIインストーラーを起動し、画面の指示に従いインストールします。

![](/images/onnx-runtime-npu-slm/2025-07-14-23-17-09.png)

![](/images/onnx-runtime-npu-slm/2025-07-14-23-17-21.png)

![](/images/onnx-runtime-npu-slm/2025-07-14-23-17-31.png)

![](/images/onnx-runtime-npu-slm/2025-07-14-23-17-43.png)

![](/images/onnx-runtime-npu-slm/2025-07-14-23-17-57.png)

![](/images/onnx-runtime-npu-slm/2025-07-15-15-34-04.png)

![](/images/onnx-runtime-npu-slm/2025-07-15-15-34-42.png)

### Python環境の構築

インストールされているminiforgeのターミナルを開き、専用環境を作成します。
```powershell
conda create -n phi4-onnx python=3.11 -y
conda activate phi4-onnx
```

:::details 実行結果
```powershell
20_slm\onnx-runtime-npu-slm > conda create -n phi4-onnx python=3.11 -y
Channels:
 - conda-forge
Platform: win-64
Collecting package metadata (repodata.json): done
Solving environment: done

## Package Plan ##

  environment location: C:\Users\nom40\miniforge3\envs\phi4-onnx

  added / updated specs:
    - python=3.11


The following packages will be downloaded:

    package                    |            build
    ---------------------------|-----------------
    python-3.11.13             |h3f84c4b_0_cpython        17.4 MB  conda-forge
    setuptools-80.9.0          |     pyhff2d567_0         731 KB  conda-forge
    ------------------------------------------------------------
                                           Total:        18.1 MB

done
#
# To activate this environment, use
#
#     $ conda activate phi4-onnx
#
# To deactivate an active environment, use
#
#     $ conda deactivate
20_slm\onnx-runtime-npu-slm > conda activate phi4-onnx
```
:::

### Hugging Face CLI

Hugging Face の Web画面にログインしたのち、Access Token を作成します。
![](/images/onnx-runtime-npu-slm/2025-07-15-22-20-22.png)

Write権限を付けます。
![](/images/onnx-runtime-npu-slm/2025-07-15-22-21-09.png)

AccessTokenをコピーして控えておきます。

Hugging Face CLI のインストール
```powershell
pip install -U "huggingface_hub[cli]"
```

認証設定をします。Write権限トークンを使います。
```powershell
huggingface-cli login
```

:::details 実行結果
```powershell
(phi4-onnx) C:\Users\nom40>huggingface-cli login

    _|    _|  _|    _|    _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|_|_|_|    _|_|      _|_|_|  _|_|_|_|
    _|    _|  _|    _|  _|        _|          _|    _|_|    _|  _|            _|        _|    _|  _|        _|
    _|_|_|_|  _|    _|  _|  _|_|  _|  _|_|    _|    _|  _|  _|  _|  _|_|      _|_|_|    _|_|_|_|  _|        _|_|_|
    _|    _|  _|    _|  _|    _|  _|    _|    _|    _|    _|_|  _|    _|      _|        _|    _|  _|        _|
    _|    _|    _|_|      _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|        _|    _|    _|_|_|  _|_|_|_|

    A token is already saved on your machine. Run `huggingface-cli whoami` to get more information or `huggingface-cli logout` if you want to log out.
    Setting a new token will erase the existing one.
    To log in, `huggingface_hub` requires a token generated from https://huggingface.co/settings/tokens .
Token can be pasted using 'Right-Click'.
Enter your token (input will not be visible):
Add token as git credential? (Y/n) Y
Token is valid (permission: write).
The token `onnx-npu-slm` has been saved to C:\Users\nom40\.cache\huggingface\stored_tokens
Your token has been saved in your configured git credential helpers (manager).
Your token has been saved to C:\Users\nom40\.cache\huggingface\token
Login successful.
The current active token is: `onnx-npu-slm`
```
:::

ログイン状態を確認しておきましょう。
```powershell
huggingface-cli whoami
```


## 必要パッケージのインストール

```powershell
pip install onnx torch onnxruntime-genai transformers
pip install accelerate huggingface-hub pandas numpy psutil
```

### 事前最適化済みモデルの利用（推奨）

Microsoft公式が提供する最適化済みONNXモデルを使用することで、変換作業を大幅に簡素化できます。

```powershell
# Microsoft公式のONNXモデルダウンロード
huggingface-cli download microsoft/Phi-4-mini-instruct-onnx --include cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/* --local-dir .
```

:::details 実行結果
```powershell
20_slm\onnx-runtime-npu-slm > huggingface-cli download microsoft/Phi-4-mini-instruct-onnx --include cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/* --local-dir .
Fetching 11 files:   0%|                                                                            | 0/11 [00:00<?, ?it/s]Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/model.onnx' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\ihhw_uFzBe-Y54_HOJQmXx4GS8A=.701aa5d185b6a782bc27104a990dd5b634fa507840b7c42f7ee6f1fb812d0b83.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/special_tokens_map.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\ahkChHUJFxEmOdq5GDFEmerRzCY=.aff38493227d813e29fcf8406e8e90062f1f031aa47d589325e9c31d89ac7cc3.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/config.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\8_PA_wEVGiVa2goH2H4KQOQpvVY=.ac65d86061d3d0d704ee2511fd0eb8713ef19eb6eedba17c3080a4165d5b933b.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/model.onnx.data' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\Lzxw0O44RMmhTgKWeQQ-MMzHFnE=.cb0267fa60befa1a4ade8c98b6d32a3d67f51abbd307c7f793f132e8d9092131.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/genai_config.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\yDyKFBRCOr3XTWAm4EHNQUX0s3Y=.0fcfa1e663f2bc867f8dc62fae65dd0924f0a4d68b43d1234df742dd19171470.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/added_tokens.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\SeqzFlf9ZNZ3or_wZAOIdsM3Yxw=.d4f2aceb0f20b71dd1f4bcc7e052e4412946bf281840b8f83d39f259571af486.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/merges.txt' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\PtHk0z_I45atnj23IIRhTExwT3w=.dcecc4524288b351bbd0da8028e74e9b5bcdb9b5.incomplete'
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/configuration_phi3.py' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\vEnnZuZbPjs88GEHAS5wEyJ0R4s=.01446e12bf573a1e96c8aa9c7af73a05e2096dec.incomplete' 
configuration_phi3.py: 10.9kB [00:00, 31.5MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\configuration_phi3.py
merges.txt: 2.42MB [00:00, 12.8MB/s] ?B/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\merges.txt
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/tokenizer.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\HgM_lKo9sdSCfRtVg7MMFS7EKqo=.382cc235b56c725945e149cc25f191da667c836655efd0857b004320e90e91ea.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
genai_config.json: 100%|██████████████████████████████████████████████████████████████| 1.52k/1.52k [00:00<00:00, 17.4MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\genai_config.json0/1.52k [00:00<?, ?B/s]
special_tokens_map.json: 100%|█████████████████████████████████████████████████████████████| 587/587 [00:00<00:00, 588kB/s]
config.json: 100%|████████████████████████████████████████████████████████████████████| 2.50k/2.50k [00:00<00:00, 5.05MB/s] 
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\special_tokens_map.jsonM [00:00<?, ?B/s] 
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\config.json | 0.00/2.50k [00:00<?, ?B/s] 
added_tokens.json: 100%|██████████████████████████████████████████████████████████████████| 249/249 [00:00<00:00, 3.90MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\added_tokens.json0/4.86G [00:00<?, ?B/s] 
Fetching 11 files:   9%|██████▏                                                             | 1/11 [00:00<00:09,  1.08it/s]Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/tokenizer_config.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\vzaExXFZNBay89bvlQv-ZcI6BTg=.c565326a315fbe62cda093a59d298828c8f3f823122661325f41f3ba577a7dec.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
Downloading 'cpu_and_mobile/cpu-int4-rtn-block-32-acc-level-4/vocab.json' to '.cache\huggingface\download\cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\j3m-Hy6QvBddw8RXA1uSWl1AJ0c=.6cb65a857824fa6615bb1782d95d882617a8bbce1da0317118586b36f39e98bd.incomplete'
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
tokenizer_config.json: 100%|██████████████████████████████████████████████████████████| 2.96k/2.96k [00:00<00:00, 24.2MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\tokenizer_config.json
vocab.json: 100%|█████████████████████████████████████████████████████████████████████| 3.91M/3.91M [00:01<00:00, 2.74MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\vocab.json/4.86G [00:01<04:54, 16.4MB/s]
tokenizer.json: 100%|█████████████████████████████████████████████████████████████████| 15.5M/15.5M [00:02<00:00, 7.53MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\tokenizer.json5M [00:01<00:00, 6.74MB/s]
model.onnx: 100%|█████████████████████████████████████████████████████████████████████| 52.1M/52.1M [00:03<00:00, 15.8MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\model.onnx/4.86G [00:02<04:20, 18.4MB/s]
model.onnx.data: 100%|████████████████████████████████████████████████████████████████| 4.86G/4.86G [02:03<00:00, 39.3MB/s]
Download complete. Moving file to cpu_and_mobile\cpu-int4-rtn-block-32-acc-level-4\model.onnx.dataG [02:03<00:00, 43.9MB/s]
Fetching 11 files: 100%|███████████████████████████████████████████████████████████████████| 11/11 [02:04<00:00, 11.31s/it] 
C:\Users\nom40\Documents\PoC\20_slm\onnx-runtime-npu-slm
```
:::

### カスタムモデルの量子化

AMD Quarkを使用した効率的な量子化が可能です。

quark-aiのZipをダウンロードして回答しておきましょう。
https://quark.docs.amd.com/release-0.5.0/install.html

```powershell
# AMD Quarkを使用した4-bit量子化
pip install quark-0.5.0+fae64a406\quark-0.5.0+fae64a406-py3-none-any.whl
```

```python
# 量子化の実行
python -c "
import quark
quantizer = ModelQuantizer(
    model=model,
    quantization_config={
        'weight_bits': 4,
        'activation_bits': 8,
        'method': 'awq'
    }
)
quantized_model = quantizer.quantize()
"
```

### NPUでの実行設定

```python
import onnxruntime as ort

# Vitis AI Execution Provider の設定
providers = ['VitisAIExecutionProvider', 'CPUExecutionProvider']
session_options = ort.SessionOptions()
session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# NPU用セッションの作成
session = ort.InferenceSession(
    "phi4_quantized.onnx",
    providers=providers,
    sess_options=session_options
)
```

## 4. 性能比較データ：CPU vs NPU

### 推論速度とスループット

**AMD Ryzen AI Max+ 395での実測値**：
- **推論速度**：Intel Core Ultra 7 258V比で**2.1倍高速**
- **Time to First Token**：小規模モデルで**最大4倍**、14Bモデルで**最大12.2倍高速**
- **スループット**：50.7 tokens/second（Llama 3.2 1B）

### 電力効率

NPU使用時は**CPU電力消費を10-15%削減**し、長時間実行でのバッテリー寿命延長効果を提供します。持続的AI処理での電力効率が大幅に向上します。

### メモリ使用量

**量子化レベル別メモリ使用量**：
- **Q4 K M**（推奨）：約8GB（14Bモデル）
- **Q6/Q8**（高精度）：約12-16GB
- **最大対応**：128GB統合メモリ（Max+ 395）

Variable Graphics Memory（VGM）により、最大96GB GPU専用メモリの確保が可能です。

## 5. 実装時の注意点とトラブルシューティング

### よくある問題と解決策

**NPU認識エラー**：
```
エラー: "Unknown platform. Exiting"
解決策: 
- NPU MCDM driver (Version: 32.0.203.280以上) を確認
- BIOSでNPU有効化
- OEM固有のドライバー制限確認
```

**メモリ不足問題**：
```
エラー: "Could not find an implementation for EPContext"
解決策:
- Variable Graphics Memory (VGM)をHighに設定
- 16GB以上のVGM推奨
- modelcachekey フォルダーを削除
```

### 量子化互換性

**プラットフォーム別対応**：
- **STX (HX370)**：W8A16 + W4ABF16 サポート
- **PHX (7840HS)**：W4ABF16のみサポート
- **HPT (8845HS)**：W4ABF16のみサポート

### 現行制限事項

- **バッチサイズ固定**（batch_size=1）
- **LM Studio直接NPU対応**未実装（2025年3月時点）
- **llama.cpp ベースアプリケーション**のNPU対応限定的

## 6. 最適化のコツと推奨設定

### 用途別推奨量子化レベル

```
- 日常会話：Q4 K M（最適バランス）
- コーディング：Q6/Q8（高精度維持）
- 高精度要求：Q8（メモリ許容時）
```

### システム設定

**LM Studio設定**：
- "manually select parameters"有効化
- GPU Offload: MAX設定
- VGM: Highモード推奨

**システム最適化**：
- Windows Power Mode: Performance
- 最新AMD Software: Adrenalin Edition™
- NPU Mode: Performance（xrt-smi経由）

## 7. 開発環境とツール

### 必要なツールチェーン

**コア開発ツール**：
- **AMD Ryzen AI Software 1.5**：統合インストーラー
- **ONNX Runtime GenAI 0.7.0**：最新の推論エンジン
- **AMD Quark**：効率的な量子化ツール
- **Microsoft Olive**：自動最適化フレームワーク

**開発支援ツール**：
- **GAIA**：オープンソースLLMアプリケーション
- **Lemonade SDK**：高水準Python API
- **TurnkeyML**：ONNX最適化ツールチェーン

### 実装サンプル

```python
class Phi4NPUInference:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-4-mini-instruct")
        
        # NPU用のセッション設定
        providers = ['VitisAIExecutionProvider', 'CPUExecutionProvider']
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        self.session = ort.InferenceSession(
            model_path,
            providers=providers,
            sess_options=session_options
        )
    
    def generate_text(self, prompt, max_length=128):
        # 入力のトークン化
        inputs = self.tokenizer(
            prompt,
            return_tensors="np",
            padding=True,
            truncation=True,
            max_length=max_length
        )
        
        # NPUでの推論実行
        outputs = self.session.run(
            None,
            {
                "input_ids": inputs["input_ids"].astype(np.int64),
                "attention_mask": inputs["attention_mask"].astype(np.int64)
            }
        )
        
        # 結果のデコード
        logits = outputs[0]
        predicted_ids = np.argmax(logits, axis=-1)
        generated_text = self.tokenizer.decode(predicted_ids[0], skip_special_tokens=True)
        
        return generated_text
```

## 8. 今後の展望と課題

### 技術的改善点

**近い将来の改善予定**：
- **ROCm 7.0**（2025年Q3）でのNPUサポート拡大
- **Windows ROCm**正式サポート（2025年後半）
- **動的量子化**対応の拡充
- **バッチサイズ**可変対応

### 現在の課題

**技術的制限**：
- 第一世代NPU技術の成熟度
- ソフトウェア生態系の発展段階
- プラットフォーム間の互換性問題

**開発環境の課題**：
- 複雑な環境構築手順
- デバッグツールの不足
- ドキュメント不足

## 技術ブログ記事作成時の推奨構成

### 記事の構成案

1. **導入**：Phi-4の概要とNPU活用の意義
2. **技術背景**：AMD Ryzen AI NPUの特徴と利点
3. **実装手順**：段階的な環境構築とサンプルコード
4. **性能評価**：具体的なベンチマーク結果
5. **トラブルシューティング**：よくある問題と解決策
6. **最適化のコツ**：実用的なパフォーマンス向上手法
7. **今後の展望**：技術動向と期待される改善点

### 読者への配慮

- **基本的な手順**を丁寧に説明
- **具体的なコードサンプル**を豊富に提供
- **トラブルシューティング**情報を充実
- **性能データ**を数値で明示
- **最新情報**への継続的な更新が必要

## 結論

Microsoft Phi-4をAMD Ryzen AI NPUで動作させる技術は、2024年後半から2025年前半にかけて急速に発展しています。現時点では一部制限があるものの、電力効率と推論速度の向上により、実用的なAIアプリケーションの開発が可能です。

特に**14Bパラメータ**という適度なサイズのPhi-4は、消費者向けハードウェアでの実用的な運用に適しており、AMD Ryzen AI NPUの特性を活かした効率的な実装が期待できます。技術ブログ記事では、これらの最新動向を踏まえた実装ガイドと性能データを提供することで、読者にとって価値のある技術情報を提供できるでしょう。