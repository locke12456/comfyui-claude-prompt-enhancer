# ComfyUI Claude Prompt Enhancer

[繁體中文](README.zh-TW.md)

Three ComfyUI nodes that caption images and rewrite prompts with Claude or a local OpenAI-compatible LLM.

```
LLM Connector ──┬─→ LLM Vision ──caption──→ LLM Prompt Enhancer ─→ enhanced_prompt
                └──────────────────────────↗
```

## Install

```
cd ComfyUI/custom_nodes
git clone <this repo> comfyui-claude-prompt-enhancer
pip install -r comfyui-claude-prompt-enhancer/requirements.txt
```

## Nodes

### LLM Connector

| Provider | Inputs |
| --- | --- |
| `claude` | `model` (haiku / sonnet / opus 5.5), `api_key` (empty uses `ANTHROPIC_API_KEY`) |
| `local` | `model`, `host`, `api_key`, `think` (sent as `reasoning_effort`) |

`local` calls `{host}/v1/chat/completions`, so it works with Strata, Ollama, LM Studio, llama.cpp and vLLM. `max_tokens` applies to both.

### LLM Vision

Captions `image` with a `vision` preset. The caption can feed the enhancer's `prompt`. `instruction` adds optional notes.

### LLM Prompt Enhancer

Rewrites `prompt` with an `enhancer` preset. `image` is optional and is sent along, for example as the first frame for MiniMax I2VA.

Presets: `anima sfw/nsfw`, `moss image`, `qwen image sfw/nsfw`, `minimax i2va sfw/nsfw`.

### MiniMax Picture Combine

Collects 1-9 pictures. A new `picture_N` slot appears as each one is connected. Each slot takes an image or a caption string, such as an LLM Vision output or cache, and is labeled `<Picture 1>` to `<Picture N>` in slot order. Captions are sent as text in place of the image; every frame of an image batch counts as one picture.

### MiniMax Ref2VA / MiniMax FL2VA

Take `llm`, `pictures` from the combine node and `prompt`, and write a MiniMax H3 Ref2VA or FL2VA prompt. FL2VA uses Picture 1 as the first frame and Picture 2 as the last frame, at `last_frame_seconds`.

## Saving and cache

All text nodes share these inputs:

- `save_format`: `txt`, `json` or `none`. Files go to `output/claude-prompt-enhancer/vision/` (LLM Vision) or `output/claude-prompt-enhancer/text/` (other nodes) as `{datetime}-{preset}-{N}pic-{short-title}-{number}.{ext}`, where N is the number of images sent. JSON also records the preset, provider, model and input.
- `subfolder` (advanced): folder under `output/`.
- `load_from_cache`: when on, the node reads `cache_file` instead of sending a request, and `llm` / `image` may stay unconnected.
- `cache_file`: dropdown of txt/json files in `output/claude-prompt-enhancer`, newest first. Press **R** to refresh after new outputs.

The result is shown on the node as a text preview.

## Editing presets

Presets live in `presets.yaml` as system prompts. Edit and restart ComfyUI. `prompts-define.md` documents the rules behind them.

## Notes

- Small local models may copy examples from a preset or skip format rules (e.g. the MiniMax `[Shot 1]` marker). Use Claude or raise `think` for the stricter presets.
- Workflows saved before `cache_file` became a dropdown hold `''`; pick `none` and save again.
