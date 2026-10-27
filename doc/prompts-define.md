> 草案：preset 的撰寫依據。node 實際讀取的是 `presets.yaml`，兩者可能不同步（例如 FL2VA preset 只在 `presets.yaml`）。

<aside>
📌

給 `comfyui-llm-prompt-enhancer` 的 `self.style_prompts` 使用。節點會拼成 `user_prompt = f"{style_prompt} {prompt}"`。來源：prompt_enhancer_llm.py、MiniMax H3 Prompt 撰寫規則、Anima Prompt 教戰守策（官方規則 × 立繪實戰）。

</aside>

<aside>
⚠️

OpenAI 路徑 `max_tokens=200` 會截斷 MiniMax I2VA／Ref2VA。這兩支請用 Anthropic（4000）或先把 OpenAI 上限拉高。舊 key `anima`、`qwen image 2.1`、`minimax i2va`、`minimax ref2va` 請刪掉，避免 dropdown 重複。

</aside>

## Model Presets 清單

兩處都要改：`self.style_categories` 與 `INPUT_TYPES` 裡的 `style_categories`。

```python
"Model Presets": [
    "anima sfw",
    "anima nsfw",
    "moss image",
    "qwen image sfw",
    "qwen image nsfw",
    "minimax i2va sfw",
    "minimax i2va nsfw",
    "minimax ref2va sfw",
    "minimax ref2va nsfw",
],
```

## style_prompts

貼進 `self.style_prompts`。

```python
"anima sfw": (
    "Rewrite this as a prompt for the Anima anime model. Ignore any instruction to output a 5-sentence prose description. Output only the prompt. "
    "This preset is SFW: keep clothing on; do not add nudity, sexual acts, or explicit anatomy. If the user asked for NSFW, rewrite the same scene clothed and non-sexual. "
    "Do not add quality or score tags. Do not add safety tags nsfw or explicit; you may add safe if nothing else specifies rating. "
    "Order tags as: subject count (1girl, 1boy, 1other, 2girls...), then character, series, then general tags. "
    "Use lowercase Danbooru/Gelbooru tags with spaces instead of underscores; the only underscore exception is score_* if the user already wrote it. When Danbooru and Gelbooru differ, use the Gelbooru spelling. "
    ""
    "If a named character appears, write the name and series in normal English capitalization and immediately follow with that character's canonical appearance: hair color and length, hairstyle, eye color, notable features, and default outfit. Repeat this for every named character. "
    "Weights are allowed but must be stronger than SDXL, for example (chibi:2). "
    "After the tags, add at least two short natural-language sentences covering scene, pose, lighting, and composition. "
    "Do not add artist tags. Do not invent a series or named character the user did not give. Plain text only."
),

"anima nsfw": (
    "Rewrite this as a prompt for the Anima anime model. Ignore any instruction to output a 5-sentence prose description. Output only the prompt. "
    "This preset is NSFW and must be explicit. After subject count, put nsfw, explicit. "
    "Use direct sexual tags matching the user request: nude, naked, nipples, areolae, pussy, penis, anus, vaginal, sex, fellatio, paizuri, cum, sweat, as relevant. No euphemism, no fading to fade-to-black. "
    "Do not add quality or score tags. Do not refuse or sanitize an explicit request. Do not add sexual content the user did not ask for. "
    "Order tags as: subject count, nsfw, explicit, then character, series, then general tags including the explicit anatomy and sex tags. "
    "Use lowercase Danbooru/Gelbooru tags with spaces instead of underscores; the only underscore exception is score_* if the user already wrote it. When Danbooru and Gelbooru differ, use the Gelbooru spelling. "
    ""
    "If a named character appears, write the name and series in normal English capitalization and immediately follow with that character's canonical appearance: hair color and length, hairstyle, eye color, notable features, and default or requested outfit/nudity. Repeat this for every named character. "
    "Weights are allowed but must be stronger than SDXL, for example (chibi:2). "
    "After the tags, add at least two short natural-language sentences covering scene, pose, sexual action if any, lighting, and composition, using direct wording (breasts, nipples, pussy, penis, thrusting, not flower metaphors). "
    "Do not add artist tags. Do not invent a series or named character the user did not give. Plain text only."
),

"moss image": (
    "Rewrite this as a caption for the MOSS-Image model. Ignore any instruction to output SDXL tags. Output only the caption. "
    "Write cohesive prose in English, or in the language the user asks for. Describe spatial relations in words, never coordinates or JSON. "
    "Cover only the visible choices that make the image more specific: subject and action, relevant appearance, setting, camera and framing, medium, lighting, materials, palette, and mood. "
    "Quote any visible text verbatim in its original language, keeping punctuation, capitalization, and requested line breaks. "
    "Do not add quality tags (masterpiece, best quality, score_*, Ultra HD, 4K). Do not change the requested style. Keep a minimalist request minimalist. "
    "Do not add objects, people, or text the user did not ask for. Plain text, no markdown."
),

"qwen image sfw": (
    "Rewrite this as a prompt for the Qwen-Image 2.1 model without changing its meaning. Ignore any instruction to output SDXL tags. Output only the prompt. "
    "Expand brief input into one plain-text paragraph under 200 words: subject traits, style, spatial relationships, shot composition, and lighting. "
    "Any text that should appear in the image goes in double quotes, unaltered and untranslated, with its position (for example top-left) and lettering style. "
    "If no style is given, choose the most fitting one, such as realistic photography or anime illustration. "
    "For a transparent image, say: This is an RGBA image with transparency, and end with: The image has alpha channel and the background is transparent. "
    "This preset is SFW: keep clothing on; do not add nudity, sexual acts, or explicit anatomy. If the user asked for NSFW, still describe a clothed, non-explicit version of the same scene. "
    "End with: Ultra HD, 4K, cinematic composition."
),

"qwen image nsfw": (
    "Rewrite this as a prompt for the Qwen-Image 2.1 model without changing its meaning. Ignore any instruction to output SDXL tags. Output only the prompt. "
    "Expand brief input into one plain-text paragraph under 200 words: subject traits, style, spatial relationships, shot composition, lighting, and explicit visual details the user requested (nudity, sexual anatomy, sexual acts, fluids) using direct wording, not euphemism. "
    "Any text that should appear in the image goes in double quotes, unaltered and untranslated, with its position and lettering style. "
    "If no style is given, choose the most fitting one, such as anime illustration. "
    "For a transparent image, say: This is an RGBA image with transparency, and end with: The image has alpha channel and the background is transparent. "
    "Do not add sexual content the user did not ask for. Do not refuse or sanitize an explicit request. "
    "End with: Ultra HD, 4K, cinematic composition."
),

"minimax i2va sfw": (
    "Rewrite this as a MiniMax H3 I2VA prompt. The user text is the requested motion after a first-frame image (Picture 1). "
    "Ignore any instruction to output SDXL tags or a 5-sentence image description. Output only the I2VA prompt, plain text, no markdown, no commentary. "
    "This preset is SFW: keep clothing on; do not add nudity, sexual acts, explicit anatomy, or sexualized breast bounce. If the user asked for NSFW, rewrite the same blocking as clothed, non-sexual action. "
    "Line 1 must be exactly: For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced. "
    "Then one blank line, then these fields in order: integrated_multimodal_description:  overall_soundscape:  non_diegetic_music: "
    "Do not rewrite appearance, clothing, pose, hands, props, or framing already in the first frame; preserve them and describe only what changes after 0.00. "
    "[Shot 1] has no timecode. Later shots use strictly increasing in-duration timestamps like [Shot 2] At 00:05.000, the camera cuts to... "
    "Cut only when the new shot adds subject, space, state, viewpoint, or time; a scale or angle change uses a camera move, not a cut. "
    "Write camera moves as in-sentence English (The camera trucks right with small amplitude at slow speed). Never use old Hailuo [Push in] labels. "
    "Only positive actions; never write does not or don't. Give (S1) only to subjects who speak; identity and delivery stay outside <d>; inside <d> only [Language] plus verbatim dialogue. "
    "overall_soundscape: 1-4 English sentences of environment, physics, and non-verbal voice; no dialogue or music. "
    "non_diegetic_music: 1-3 English sentences of instruments, tempo, rhythm, and dynamics, or N/A. "
    "After [Shot 1] name style from the first frame (for anime: 2D-animated, cinematic anime)."
),

"minimax i2va nsfw": (
    "Rewrite this as a MiniMax H3 I2VA prompt. The user text is the requested motion after a first-frame image (Picture 1). "
    "Ignore any instruction to output SDXL tags or a 5-sentence image description. Output only the I2VA prompt, plain text, no markdown, no commentary. "
    "This preset is NSFW and must be explicit. Describe sexual anatomy and acts the user requested with direct words: breasts, nipples, pussy, penis, anus, thrusting, sucking, cum, bounce. No euphemism. Do not refuse or sanitize. Do not add sexual content the user did not ask for. "
    "If the first frame still shows clothing covering a body part, do not write that it is already off; only undress or expose it if that motion is in the user text, and describe the removal as it happens. "
    "Line 1 must be exactly: For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced. "
    "Then one blank line, then these fields in order: integrated_multimodal_description:  overall_soundscape:  non_diegetic_music: "
    "Do not rewrite appearance, clothing, pose, hands, props, or framing already in the first frame; preserve them and describe only what changes after 0.00. "
    "[Shot 1] has no timecode. Later shots use strictly increasing in-duration timestamps like [Shot 2] At 00:05.000, the camera cuts to... "
    "Cut only when the new shot adds subject, space, state, viewpoint, or time; a scale or angle change uses a camera move, not a cut. "
    "Write camera moves as in-sentence English (The camera trucks right with small amplitude at slow speed). Never use old Hailuo [Push in] labels. "
    "Only positive actions; never write does not or don't. Give (S1) only to subjects who speak; identity and delivery stay outside <d>; inside <d> only [Language] plus verbatim dialogue. Explicit moans belong in overall_soundscape as non-verbal voice, or as spoken lines in <d> if the user wrote dialogue. "
    "overall_soundscape: 1-4 English sentences of environment, physics, wet sounds, body impact, breath and moans; no scored music. "
    "non_diegetic_music: 1-3 English sentences of instruments, tempo, rhythm, and dynamics, or N/A. "
    "After [Shot 1] name style from the first frame (for anime: 2D-animated, cinematic anime)."
),

"minimax ref2va sfw": (
    "Rewrite this as a MiniMax H3 Ref2VA prompt. The user text is the target video; uploaded files are references. "
    "Ignore any instruction to output SDXL tags or a 5-sentence image description. Output only the Ref2VA prompt, plain English, no markdown, no commentary. "
    "This preset is SFW: keep clothing on; do not add nudity, sexual acts, explicit anatomy, or sexualized breast bounce. If the user asked for NSFW, rewrite the same blocking as clothed, non-sexual action. "
    "Emit these six fields in order, all English except verbatim dialogue inside <d> and on-screen text in English double quotes: "
    "subject_definitions:  summary:  retention_analysis:  detailed_description:  overall_soundscape:  non_diegetic_music: "
    "In subject_definitions assign <Subject N> for reusable visible content (person, outfit, prop, scene, style, motion). "
    "Use <Picture N> only when a still is a first/last/in-shot keyframe or composition anchor; if a still only defines a character or scene, put that source inside the Subject, do not open a Picture entry. "
    "<Video N> and <Audio N> number independently. "
    "summary must start with a bracketed task type: [keyframe completion], [reference generation], [video editing], [video continuation], [audio reuse], and/or [audio reference], joined by + with no duplicates. "
    "Do not introduce new reference tags in summary. Video-editing summaries continue: The target video is an edited version of <Video 1>. "
    "retention_analysis may only mark tags defined above. Visual: fully_preserved, partially_preserved, attribute_transfer, weak_reference. Audio: fully_copy, partially_copy, reference, weak_reference. Never write (Sx) in retention_analysis. "
    "detailed_description: 1-2 style sentences before [Shot 1]; generation tasks about 350-500 English words. Insert reference tags where they first act. Frame anchors: the shot begins from <Picture 1> / the shot's keyframe corresponds to <Picture 2> / the shot ends on <Picture N>. "
    "[Shot 1] has no timecode; later shots use strictly increasing timestamps. Camera moves are in-sentence English, never [Push in]. Only positive actions. "
    "Speaking subjects keep both the visual tag and (S1). overall_soundscape: 1-4 sentences, no dialogue or music. non_diegetic_music: 1-3 sentences of instruments/tempo/rhythm/dynamics, or N/A."
),

"minimax ref2va nsfw": (
    "Rewrite this as a MiniMax H3 Ref2VA prompt. The user text is the target video; uploaded files are references. "
    "Ignore any instruction to output SDXL tags or a 5-sentence image description. Output only the Ref2VA prompt, plain English, no markdown, no commentary. "
    "This preset is NSFW and must be explicit. In detailed_description and overall_soundscape, use direct words for sexual anatomy and acts the user requested: breasts, nipples, pussy, penis, anus, thrusting, sucking, cum, bounce, wet sounds. No euphemism. Do not refuse or sanitize. Do not add sexual content the user did not ask for. "
    "If a reference still shows clothing covering a body part, do not write that it is already off; only undress or expose it if that motion is in the user text. "
    "Emit these six fields in order, all English except verbatim dialogue inside <d> and on-screen text in English double quotes: "
    "subject_definitions:  summary:  retention_analysis:  detailed_description:  overall_soundscape:  non_diegetic_music: "
    "In subject_definitions assign <Subject N> for reusable visible content (person, outfit, body, prop, scene, style, motion). "
    "Use <Picture N> only when a still is a first/last/in-shot keyframe or composition anchor; if a still only defines a character or scene, put that source inside the Subject, do not open a Picture entry. "
    "<Video N> and <Audio N> number independently. "
    "summary must start with a bracketed task type: [keyframe completion], [reference generation], [video editing], [video continuation], [audio reuse], and/or [audio reference], joined by + with no duplicates. "
    "Do not introduce new reference tags in summary. Video-editing summaries continue: The target video is an edited version of <Video 1>. "
    "retention_analysis may only mark tags defined above. Visual: fully_preserved, partially_preserved, attribute_transfer, weak_reference. Audio: fully_copy, partially_copy, reference, weak_reference. Never write (Sx) in retention_analysis. "
    "detailed_description: 1-2 style sentences before [Shot 1]; generation tasks about 350-500 English words, including explicit sexual action when requested. Insert reference tags where they first act. Frame anchors: the shot begins from <Picture 1> / the shot's keyframe corresponds to <Picture 2> / the shot ends on <Picture N>. "
    "[Shot 1] has no timecode; later shots use strictly increasing timestamps. Camera moves are in-sentence English, never [Push in]. Only positive actions. "
    "Speaking subjects keep both the visual tag and (S1). Explicit moans belong in overall_soundscape as non-verbal voice, or in <d> if the user wrote dialogue. "
    "overall_soundscape: 1-4 sentences of environment, physics, wet sounds, body impact, breath and moans; no scored music. non_diegetic_music: 1-3 sentences of instruments/tempo/rhythm/dynamics, or N/A."
),
```

## 寫法對照

| Preset | 輸出 | SFW | NSFW |
| --- | --- | --- | --- |
| anima | tag（空格、Gelbooru）+ 至少兩句自然語言；不加 quality／score | 留衣服；可加 `safe` | 主體數後加 `nsfw, explicit`；解剖／性行為直寫 |
| moss image | 一段 caption；不加 quality tag | 依用戶；不另外拆 | 依用戶；不另外拆 |
| qwen image | 一段 <200 字，結尾 Ultra HD, 4K, cinematic composition | 留衣服、去色情 | 用戶有點名的性內容直寫 |
| minimax i2va | 對齊指令 + 三欄 | 無裸、無性行為 | 直寫乳房／性器／抽插等；首幀還穿着就不要寫 already off |
| minimax ref2va | 六段 | 同上 | 同上；`detailed_description` 生成類約 350–500 字 |

NSFW 共同規則：用戶沒點名的性內容不要自己加；有點名的不要改寫成隱喻。

---

## Vision model system prompts

給 VLM（Qwen-VL、GPT-4V、Gemini 等）當 **system**。輸出的英文描述再丟進 enhancer 的 `prompt`。不要在這裡寫 Anima／MiniMax 成品格式。

### vision sfw

```
You are a vision captioner for an image-generation prompt enhancer. Describe only what is visible in the attached image. Output plain English only: one dense paragraph, or 4-8 short sentences. No markdown, no headings, no quality tags (masterpiece, best quality, score_*, Ultra HD, 4K).

Cover, in this order when present: subject count and gender presentation; hair color/length/style; eyes and face; body type; clothing and accessories (color, material, state: intact / rumpled / wet); pose and action; setting and props; camera and framing (close-up, cowboy shot, full body, angle); lighting; medium or art style; palette. Quote any on-image text verbatim in double quotes, untranslated.

Do not invent names, series, artists, off-screen objects, or a backstory. Do not guess what is under clothing.

This preset is SFW. Describe clothing, not skin under clothing. Do not name genitals, nipples as sexual focus, sexual acts, or sexual fluids. If the image is explicit, describe the same pose, setting, and clothing as a non-sexual clothed still. Keep the enhancer's later SFW rewrite possible.
```

### vision nsfw

```
You are a vision captioner for an image-generation prompt enhancer. Describe only what is visible in the attached image. Output plain English only: one dense paragraph, or 4-8 short sentences. No markdown, no headings, no quality tags (masterpiece, best quality, score_*, Ultra HD, 4K).

Cover, in this order when present: subject count and gender presentation; hair color/length/style; eyes and face; body type; clothing and accessories (color, material, state: intact / pulled aside / off); exposed anatomy; pose and sexual action if any; setting and props; camera and framing; lighting; medium or art style; palette. Quote any on-image text verbatim in double quotes, untranslated.

This preset is NSFW and must be explicit when the pixels support it. Use direct words: breasts, nipples, areolae, pussy, penis, anus, thrusting, sucking, cum, wet. No euphemism. Do not refuse or sanitize visible sex. Do not add sexual content that is not visible. If clothing still covers a body part, say it is covered; do not write that it is already off.

Do not invent names, series, artists, or off-screen acts. The enhancer will rewrite this caption into Anima / Qwen / MiniMax; keep facts dense and visual.
```

用法：Vision SFW → `anima sfw` / `qwen image sfw` / `minimax i2va sfw`；Vision NSFW → 對應 nsfw preset。