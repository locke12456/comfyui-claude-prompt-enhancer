# ComfyUI Claude Prompt Enhancer

[English](README.md)

三個 ComfyUI node，用 Claude 或本地 OpenAI 相容 LLM 描述圖片、改寫 prompt。

```
LLM Connector ──┬─→ LLM Vision ──caption──→ LLM Prompt Enhancer ─→ enhanced_prompt
                └──────────────────────────↗
```

## 安裝

```
cd ComfyUI/custom_nodes
git clone https://github.com/locke12456/comfyui-claude-prompt-enhancer.git
pip install -r comfyui-claude-prompt-enhancer/requirements.txt
```

## Node

### LLM Connector

| Provider | 欄位 |
| --- | --- |
| `claude` | `model`（haiku／sonnet／opus 5.5）、`api_key`（留空會用 `ANTHROPIC_API_KEY`） |
| `local` | `model`、`host`、`api_key`、`think`（送出時為 `reasoning_effort`） |

`local` 呼叫 `{host}/v1/chat/completions`，Strata、Ollama、LM Studio、llama.cpp、vLLM 都能用。`max_tokens` 兩種 provider 共用。

### LLM Vision

用 `vision` preset 描述 `image`，caption 可以接到 Enhancer 的 `prompt`。`instruction` 可附加說明。

### LLM Prompt Enhancer

用 `enhancer` preset 改寫 `prompt`。`image` 選填，會一起送出，例如當作 MiniMax I2VA 的首幀。

Preset：`anima sfw/nsfw`、`moss image`、`qwen image sfw/nsfw`、`minimax i2va sfw/nsfw`。

`next_state` 可搭配任何 preset：接上的圖片是目前狀態，`prompt` 寫接下來發生的事（例如「小貓跳起來」），輸出所選 preset 格式的、變化後那一刻的 prompt，其餘保持不變。

### MiniMax Picture Combine

收集 1–9 張 picture，每接上一個就會多出下一個 `picture_N` 欄位。每格可接圖片或 caption 文字（例如 LLM Vision 的輸出或快取），依欄位順序標為 `<Picture 1>` 到 `<Picture N>`。caption 會以文字代替圖片送出；圖片 batch 裡的每一幀各算一張。

### MiniMax Ref2VA／MiniMax FL2VA

輸入 `llm`、combine node 的 `pictures` 和 `prompt`，寫出 MiniMax H3 Ref2VA 或 FL2VA prompt。FL2VA 以 Picture 1 為首幀、Picture 2 為尾幀，尾幀時間由 `last_frame_seconds` 指定。

## 存檔與快取

所有文字 node 共用以下欄位：

- `save_format`：`txt`、`json` 或 `none`。存到 `output/claude-prompt-enhancer/vision/`（LLM Vision）或 `output/claude-prompt-enhancer/text/`（其他 node），檔名為 `{日期時間}-{preset}-{N}pic-{短標題}-{編號}.{副檔名}`，N 是送出的圖片數。json 另外記錄 preset、provider、model 和輸入。
- `subfolder`（advanced）：`output/` 底下的資料夾。
- `load_from_cache`：開啟時讀取 `cache_file`，不送 request，`llm`／`image` 可以不接。
- `cache_file`：`output/claude-prompt-enhancer` 裡的 txt／json 下拉選單，最新的在最上面。有新檔案時按 **R** 更新。

結果會以文字預覽顯示在 node 上。

## Workflow

`workflows/` 每個功能各一份 API 格式範例：`vision`、`prompt-enhancer`、`vision-to-enhancer`、`minimax-i2va`、`minimax-ref2va`、`minimax-fl2va`，拖進 ComfyUI 即可。預設連本地 Strata，圖片取自 `input/`，請依自己的環境調整。

## 修改 preset

Preset 以 system prompt 形式放在 `presets.yaml`，改完重啟 ComfyUI 即可。`doc/prompts-define.md` 是撰寫 preset 時的草案，node 實際讀取的是 `presets.yaml`。

## 注意

- 本地小模型可能照抄 preset 裡的範例，或漏掉格式規則（例如 MiniMax 的 `[Shot 1]`）。規則嚴格的 preset 建議用 Claude 或調高 `think`。
- `cache_file` 改成下拉選單之前存的 workflow 會留著 `''`，選 `none` 後另存即可。
