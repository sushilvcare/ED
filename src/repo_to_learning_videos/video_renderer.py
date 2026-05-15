from __future__ import annotations

import asyncio
import re
import subprocess
import textwrap
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

from .models import FeatureModule

WIDTH = 1280
HEIGHT = 720
FPS = 30
BG_COLOR = (16, 20, 28)
TITLE_COLOR = (98, 170, 255)
TEXT_COLOR = (235, 240, 245)


def render_module_video(
    module: FeatureModule,
    voiceover_markdown: str,
    module_video_dir: Path,
    voice: str,
    snippets: dict[str, str] | None = None,
    narration_style: str = "english-neutral",
) -> Path:
    slides = _build_slides(module, voiceover_markdown, snippets or {}, narration_style)
    assets_dir = module_video_dir / "_render"
    assets_dir.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for idx, slide in enumerate(slides, start=1):
        image_path = assets_dir / f"slide-{idx:02d}.png"
        audio_path = assets_dir / f"slide-{idx:02d}.mp3"
        clip_path = assets_dir / f"clip-{idx:02d}.mp4"
        _render_slide_image(slide["title"], slide["body"], image_path)
        _synthesize_tts(slide["narration"], audio_path, voice)
        _render_clip(image_path, audio_path, clip_path)
        clip_paths.append(clip_path)

    video_path = module_video_dir / f"{module.slug}.mp4"
    _concat_clips(clip_paths, assets_dir / "concat.txt", video_path)
    return video_path


def _build_slides(
    module: FeatureModule,
    voiceover_markdown: str,
    snippets: dict[str, str],
    narration_style: str,
) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = [
        {
            "title": module.name,
            "body": f"Difficulty: {module.difficulty.value}\nModule slug: {module.slug}",
            "narration": f"This video teaches {module.name} as a {module.difficulty.value} module.",
        }
    ]
    for raw in voiceover_markdown.split("## "):
        cleaned = raw.strip()
        if not cleaned:
            continue
        lines = cleaned.splitlines()
        title = _strip_markdown(lines[0])
        body = "\n".join(_strip_markdown(line) for line in lines[1:] if line.strip())[:900]
        if not body:
            continue
        narration = re.sub(r"\s+", " ", body).strip()
        sections.append({"title": title, "body": body, "narration": narration})

    code_slides = _build_code_teacher_slides(snippets, narration_style)
    if code_slides:
        sections.extend(code_slides)

    return sections[:14]


def _build_code_teacher_slides(snippets: dict[str, str], narration_style: str) -> list[dict[str, str]]:
    if not snippets:
        return []

    first_file = next(iter(snippets.keys()))
    snippet = snippets[first_file]
    lines: list[str] = []
    for line in snippet.splitlines():
        stripped = line.rstrip()
        if not stripped:
            continue
        if stripped.startswith("//") or stripped.startswith("#"):
            continue
        lines.append(stripped)
        if len(lines) >= 8:
            break

    slides: list[dict[str, str]] = []
    for idx, code_line in enumerate(lines, start=1):
        explanation = _explain_code_line(code_line, narration_style)
        if narration_style in {"hindi-indian-man", "hindi-teacher-simple"}:
            title = f"Code Dashboard Line {idx}"
            body = (
                f"File: {first_file}\n"
                f"Line {idx}: {code_line}\n\n"
                f"Simple Explain: {explanation}"
            )
            narration = (
                f"Ab dashboard pe line number {idx} dekhte hain. "
                f"Code hai: {code_line}. "
                f"Is line ka matlab: {explanation}"
            )
        else:
            title = f"Code Walkthrough Line {idx}"
            body = f"File: {first_file}\nLine {idx}: {code_line}\n\nExplanation: {explanation}"
            narration = f"Line {idx} reads {code_line}. This means: {explanation}"

        slides.append({"title": title, "body": body, "narration": narration})
    return slides


def _explain_code_line(code_line: str, narration_style: str) -> str:
    trimmed = code_line.strip()
    if narration_style in {"hindi-indian-man", "hindi-teacher-simple"}:
        if "if " in trimmed or trimmed.startswith("if(") or trimmed.startswith("if ("):
            return "yeh condition check karti hai, taaki galat data aage process na ho."
        if "return" in trimmed:
            return "yahan function result wapas bhej raha hai, isse flow clear aur predictable rehta hai."
        if "=" in trimmed and "==" not in trimmed:
            return "is line me value assign ho rahi hai, taaki next logic ke liye data ready rahe."
        if "await " in trimmed:
            return "yahan async call ka wait ho raha hai, taaki next step sahi response ke saath chale."
        if "throw" in trimmed:
            return "error case handle karne ke liye yahan exception throw kiya gaya hai."
        return "yeh line business logic ka hissa hai, jo request flow ko step by step control karti hai."

    if "if " in trimmed:
        return "this condition guards the flow and prevents invalid processing."
    if "return" in trimmed:
        return "this returns the computed output to the caller."
    if "=" in trimmed and "==" not in trimmed:
        return "this assigns a value used by downstream logic."
    if "await " in trimmed:
        return "this waits for async work to finish before continuing."
    return "this line contributes to the module runtime flow."


def _render_slide_image(title: str, body: str, output_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("DejaVuSans.ttf", 42)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 24)
    except OSError:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
    draw.text((70, 55), title, fill=TITLE_COLOR, font=font_title)
    wrapped = "\n".join(textwrap.wrap(body, width=70))
    draw.multiline_text((70, 150), wrapped, fill=TEXT_COLOR, font=font_body, spacing=10)
    img.save(output_path, format="PNG")


def _synthesize_tts(text: str, output_path: Path, voice: str) -> None:
    sanitized = text.strip() or "Module content."
    asyncio.run(_save_tts(sanitized, output_path, voice))


async def _save_tts(text: str, output_path: Path, voice: str) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(output_path))


def _render_clip(image_path: Path, audio_path: Path, output_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-shortest",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def _concat_clips(clip_paths: list[Path], list_path: Path, output_path: Path) -> None:
    list_content = "\n".join(f"file '{clip.as_posix()}'" for clip in clip_paths)
    list_path.write_text(list_content, encoding="utf-8")
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def _strip_markdown(text: str) -> str:
    text = re.sub(r"`", "", text)
    text = re.sub(r"^\s*[-*#]+\s*", "", text)
    return text.strip()

