# CLAUDE.md

ComfyUI custom nodes that caption images and rewrite prompts with Claude or a local OpenAI-compatible LLM. Also follow `../../AGENTS.md` (ComfyUI's engineering rules).

## Layout

- `nodes.py`: all nodes (V3 `comfy_api.latest` schema) and helpers. `__init__.py` only exposes `comfy_entrypoint`.
- `presets.yaml`: every system prompt, in sections `enhancer`, `vision`, `ref2va`, `fl2va`, plus the shared `next_state` instruction. Each node's preset dropdown is the keys of its section. Never hardcode prompt text in Python.
- `doc/prompts-define.md`: the user's draft the presets came from. It is not loaded and may lag behind `presets.yaml`.
- `workflows/`: one API-format sample per feature. A copy lives in `output/claude-prompt-enhancer/workflows/`; update both when inputs change.

## Nodes

- `LLMConnector`: `provider` is a DynamicCombo (`claude` / `local`) and outputs an `LLM_CONNECTION` dict. `local` posts to `{host}/v1/chat/completions`. Defaults match the user's Strata server (`127.0.0.1:8080`, key `1234`, model `rvn-iq3s`, `think` sent as `reasoning_effort`).
- `LLMPromptEnhancer` has `next_state`, which appends `presets.yaml` `next_state.instruction` to any enhancer preset.
- `LLMVision`, `LLMPromptEnhancer`, `MiniMaxRef2VA`, `MiniMaxFL2VA`: text nodes sharing `file_inputs()` (`save_format`, `subfolder`, `load_from_cache`, `cache_file`). They return a STRING plus `ui.PreviewText`. `llm` and image inputs are optional so the cache path works without them.
- `MiniMaxPictureCombine`: Autogrow `picture_N` slots (max 9), each IMAGE or STRING. Outputs a list of `("image", b64)` / `("caption", text)`. `picture_prompt` labels them `<Picture N>` in slot order and only real images are attached.

## Conventions

- Outputs go to `output/claude-prompt-enhancer/{vision|text}/{time}-{preset}-{N}pic-{title}-{NNN}.{txt|json}`. `cache_file` lists that tree recursively, skipping `workflows/`. Any path from a combo or string goes through `output_path()` for containment.
- Let LLM errors raise. Do not fall back to the input prompt.
- Changing an input's type breaks saved workflow values (e.g. `cache_file` went from string `''` to a combo with `none`). Mention this to the user when it happens.
- API-format input keys for dynamic inputs are dotted: `provider.model`, `pictures.picture_0`.
- Small local models often copy preset examples or skip MiniMax format rules. Treat that as a model limit, not a node bug, unless the user asks to tune presets.

## Testing

No test suite. Smoke-test from `D:\AI\ComfyUI` with the embedded Python, calling node classes directly:

```
../python_embeded/python.exe -c "import sys; sys.path.insert(0, 'custom_nodes'); import importlib; m = importlib.import_module('comfyui-claude-prompt-enhancer.nodes'); ..."
```

Use images from `ComfyUI/input/`. Real LLM calls need Strata running; check with `curl -H "Authorization: Bearer 1234" http://127.0.0.1:8080/v1/models`. Delete test outputs you create.

## Editing gotchas

- On Windows, Python `open(..., "w")` writes CRLF. When patching files from scripts, read with `newline=""` and write with `newline="\n"`, or use the Edit tool.
- Commit messages use the short `Add ...` / `Fix ...` style. Push only when asked; the remote is `origin` on `master`.
