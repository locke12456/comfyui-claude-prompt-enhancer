from .nodes import PromptEnhancerExtension


async def comfy_entrypoint() -> PromptEnhancerExtension:
    return PromptEnhancerExtension()
