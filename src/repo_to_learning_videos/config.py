from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class PipelineConfig:
    repo_source: str
    output_dir: Path
    max_snippets_per_module: int = 4
    max_lines_per_snippet: int = 120
    generate_videos: bool = True
    narration_styles: list[str] | None = None
    tts_voice_overrides: dict[str, str] | None = None

