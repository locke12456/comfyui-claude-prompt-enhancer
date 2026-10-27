import base64
import io as pyio
import json
import os
import re
from datetime import datetime

import anthropic
import requests
import yaml
from PIL import Image

import folder_paths
from comfy_api.latest import ComfyExtension, io, ui

with open(os.path.join(os.path.dirname(__file__), "presets.yaml"), encoding="utf-8") as f:
    PRESETS = yaml.safe_load(f)

CLAUDE_MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]

LLMConnection = io.Custom("LLM_CONNECTION")


def encode_images(image):
    out = []
    for frame in image:
        buf = pyio.BytesIO()
        Image.fromarray((frame.cpu().numpy() * 255).clip(0, 255).astype("uint8")).save(buf, format="PNG")
        out.append(base64.b64encode(buf.getvalue()).decode())
    return out


def chat(llm, system, text, images=()):
    if llm["provider"] == "claude":
        content = [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b}} for b in images]
        content.append({"type": "text", "text": text})
        extra = {"output_config": {"effort": "low"}}
        # Opus 5.5 cannot turn thinking off, so it only gets low effort.
        if llm["model"] == "claude-sonnet-5-5":
            extra["thinking"] = {"type": "between_tools"}
        elif llm["model"] == "claude-haiku-5-5":
            extra["thinking"] = {"type": "disabled"}
        response = anthropic.Anthropic(api_key=llm["api_key"]).messages.create(
            model=llm["model"], max_tokens=llm["max_tokens"], system=system,
            messages=[{"role": "user", "content": content}], **extra)
        return "".join(b.text for b in response.content if b.type == "text").strip()

    # Strata, Ollama, LM Studio, llama.cpp and vLLM all serve the OpenAI chat completions endpoint.
    content = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b}"}} for b in images]
    content.append({"type": "text", "text": text})
    response = requests.post(f"{llm['host'].rstrip('/')}/v1/chat/completions", timeout=3600,
                             headers={"Authorization": f"Bearer {llm['api_key']}"}, json={
        "model": llm["model"], "max_tokens": llm["max_tokens"], "reasoning_effort": llm["think"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": content}],
    })
    response.raise_for_status()
    return (response.json()["choices"][0]["message"]["content"] or "").strip()


def output_path(relative):
    path = os.path.abspath(os.path.join(folder_paths.get_output_directory(), relative))
    if os.path.commonpath((path, folder_paths.get_output_directory())) != folder_paths.get_output_directory():
        raise ValueError(f"Path must stay inside the output directory: {relative}")
    return path


def cached_files():
    root = output_path("claude-prompt-enhancer")
    files = []
    for dirpath, _, names in os.walk(root):
        files += [os.path.relpath(os.path.join(dirpath, n), root).replace("\\", "/") for n in names if n.endswith((".txt", ".json"))]
    return ["none"] + sorted(files, reverse=True)


def load_cached(cache_file):
    if cache_file == "none":
        raise ValueError("Pick a cache_file to load")
    cache_file = os.path.join("claude-prompt-enhancer", cache_file)
    with open(output_path(cache_file), encoding="utf-8") as f:
        if cache_file.endswith(".json"):
            return json.load(f)["output"]
        return f.read()


def save_output(save_format, subfolder, preset, llm, input_text, output_text):
    if save_format == "none":
        return
    out_dir = output_path(subfolder)
    os.makedirs(out_dir, exist_ok=True)
    now = datetime.now()
    title = "-".join(re.findall(r"[a-z0-9]+", (input_text or output_text).lower())[:5]) or "untitled"
    stem = f"{now:%Y%m%d-%H%M%S}-{title}"
    number = 1
    while os.path.exists(os.path.join(out_dir, f"{stem}-{number:03}.{save_format}")):
        number += 1
    with open(os.path.join(out_dir, f"{stem}-{number:03}.{save_format}"), "w", encoding="utf-8") as f:
        if save_format == "txt":
            f.write(output_text)
        else:
            json.dump({"datetime": now.isoformat(timespec="seconds"), "preset": preset, "provider": llm["provider"],
                       "model": llm["model"], "input": input_text, "output": output_text}, f, ensure_ascii=False, indent=2)


def file_inputs():
    return [
        io.Combo.Input("save_format", options=["txt", "json", "none"], default="txt"),
        io.String.Input("subfolder", default="claude-prompt-enhancer", advanced=True),
        io.Boolean.Input("load_from_cache", default=False, tooltip="Read cache_file instead of calling the LLM."),
        io.Combo.Input("cache_file", options=cached_files(), tooltip="Files in output/claude-prompt-enhancer, newest first. "
                       "Refresh the node definitions (R) to see new files."),
    ]


class LLMConnector(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="LLMConnector",
            display_name="LLM Connector",
            category="conditioning/prompt",
            inputs=[
                io.DynamicCombo.Input("provider", options=[
                    io.DynamicCombo.Option("claude", [
                        io.Combo.Input("model", options=CLAUDE_MODELS, default="claude-haiku-5-5"),
                        io.String.Input("api_key", default="", tooltip="Leave empty to use ANTHROPIC_API_KEY."),
                    ]),
                    io.DynamicCombo.Option("local", [
                        io.String.Input("model", default="rvn-iq3s"),
                        io.String.Input("host", default="http://127.0.0.1:8080",
                                        tooltip="Any OpenAI-compatible server: Strata, Ollama, LM Studio, llama.cpp, vLLM."),
                        io.String.Input("api_key", default="1234"),
                        io.Combo.Input("think", options=["off", "low", "medium", "high"], default="off",
                                       tooltip="Sent as reasoning_effort."),
                    ]),
                ]),
                io.Int.Input("max_tokens", default=4000, min=1, max=64000),
            ],
            outputs=[LLMConnection.Output("llm")],
        )

    @classmethod
    def execute(cls, provider, max_tokens) -> io.NodeOutput:
        llm = {"provider": provider["provider"], "model": provider["model"].strip(), "max_tokens": max_tokens}
        if llm["provider"] == "claude":
            llm["api_key"] = provider["api_key"].strip() or os.environ.get("ANTHROPIC_API_KEY", "")
            if not llm["api_key"]:
                raise ValueError("Set api_key or ANTHROPIC_API_KEY first")
        else:
            llm.update(host=provider["host"].strip(), api_key=provider["api_key"].strip(), think=provider["think"])
        return io.NodeOutput(llm)


class LLMVision(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="LLMVision",
            display_name="LLM Vision",
            category="conditioning/prompt",
            inputs=[
                LLMConnection.Input("llm", optional=True),
                io.Image.Input("image", optional=True),
                io.Combo.Input("preset", options=list(PRESETS["vision"])),
                io.String.Input("instruction", multiline=True, default="", optional=True,
                                tooltip="Extra notes sent with the image."),
                *file_inputs(),
            ],
            outputs=[io.String.Output("caption")],
        )

    @classmethod
    def execute(cls, preset, save_format, subfolder, load_from_cache, cache_file, llm=None, image=None, instruction="") -> io.NodeOutput:
        if load_from_cache:
            caption = load_cached(cache_file)
        else:
            if llm is None or image is None:
                raise ValueError("Connect llm and image, or turn on load_from_cache")
            caption = chat(llm, PRESETS["vision"][preset], instruction or "Describe this image.", encode_images(image))
            save_output(save_format, subfolder, preset, llm, instruction, caption)
        return io.NodeOutput(caption, ui=ui.PreviewText(caption))


class LLMPromptEnhancer(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="LLMPromptEnhancer",
            display_name="LLM Prompt Enhancer",
            category="conditioning/prompt",
            inputs=[
                LLMConnection.Input("llm", optional=True),
                io.String.Input("prompt", multiline=True, default=""),
                io.Combo.Input("preset", options=list(PRESETS["enhancer"])),
                io.Image.Input("image", optional=True, tooltip="First frame or references for the MiniMax presets."),
                *file_inputs(),
            ],
            outputs=[io.String.Output("enhanced_prompt")],
        )

    @classmethod
    def execute(cls, prompt, preset, save_format, subfolder, load_from_cache, cache_file, llm=None, image=None) -> io.NodeOutput:
        if load_from_cache:
            enhanced = load_cached(cache_file)
        else:
            if llm is None:
                raise ValueError("Connect llm, or turn on load_from_cache")
            images = encode_images(image) if image is not None else ()
            enhanced = chat(llm, PRESETS["enhancer"][preset], prompt, images)
            save_output(save_format, subfolder, preset, llm, prompt, enhanced)
        return io.NodeOutput(enhanced, ui=ui.PreviewText(enhanced))


class PromptEnhancerExtension(ComfyExtension):
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [LLMConnector, LLMVision, LLMPromptEnhancer]
