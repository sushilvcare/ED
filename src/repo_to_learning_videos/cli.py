from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from .config import PipelineConfig
from .pipeline import RepoToCoursePipeline

STYLE_TO_VOICE = {
    "english-neutral": "en-US-AndrewNeural",
    "hindi-teacher-simple": "hi-IN-MadhurNeural",
    "hindi-indian-man": "hi-IN-MadhurNeural",
    "urdu-female": "ur-PK-UzmaNeural",
}


def _int_env(name: str, fallback: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    try:
        return int(raw)
    except ValueError:
        return fallback


def _bool_env(name: str, fallback: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _list_env(name: str, fallback: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None:
        return fallback
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or fallback


def _voice_overrides(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    result: dict[str, str] = {}
    pairs = [item.strip() for item in raw.split(",") if item.strip()]
    for pair in pairs:
        if ":" not in pair:
            continue
        style, voice = pair.split(":", 1)
        style_key = style.strip()
        voice_value = voice.strip()
        if style_key and voice_value:
            result[style_key] = voice_value
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo2course",
        description="Generate teachable learning modules from a code repository.",
    )
    parser.add_argument(
        "--repo",
        default=os.getenv("REPO_SOURCE"),
        help="Local repository path or HTTPS GitHub URL",
    )
    parser.add_argument(
        "--output",
        default=os.getenv("OUTPUT_DIR", "output"),
        help="Directory to write generated artifacts",
    )
    parser.add_argument(
        "--max-snippets",
        type=int,
        default=_int_env("MAX_SNIPPETS", 4),
        help="Maximum snippets per detected module",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=_int_env("MAX_LINES", 120),
        help="Maximum lines included in a single snippet",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity",
    )
    parser.add_argument(
        "--generate-videos",
        default=_bool_env("GENERATE_VIDEOS", True),
        action=argparse.BooleanOptionalAction,
        help="Generate playable MP4 videos per module",
    )
    parser.add_argument(
        "--narration-styles",
        default=",".join(_list_env("NARRATION_STYLES", ["hindi-teacher-simple", "english-neutral"])),
        help="Comma-separated narration styles (e.g. hindi-teacher-simple,english-neutral)",
    )
    parser.add_argument(
        "--tts-voice",
        default=os.getenv("TTS_VOICE"),
        help="Single fallback Edge TTS voice id for all styles",
    )
    parser.add_argument(
        "--tts-voice-map",
        default=os.getenv("TTS_VOICE_MAP"),
        help="Per-style voice overrides: style:voice,style:voice",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.repo:
        parser.error("Missing repo source. Use --repo or set REPO_SOURCE.")

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        requested_styles = [item.strip() for item in args.narration_styles.split(",") if item.strip()]
        if not requested_styles:
            parser.error("At least one narration style is required.")
        unknown = [item for item in requested_styles if item not in STYLE_TO_VOICE]
        if unknown:
            parser.error(f"Unsupported narration styles: {', '.join(unknown)}")
        voice_map = _voice_overrides(args.tts_voice_map)
        for style in requested_styles:
            if style not in voice_map:
                voice_map[style] = args.tts_voice or STYLE_TO_VOICE[style]

        config = PipelineConfig(
            repo_source=args.repo,
            output_dir=Path(args.output),
            max_snippets_per_module=args.max_snippets,
            max_lines_per_snippet=args.max_lines,
            generate_videos=args.generate_videos,
            narration_styles=requested_styles,
            tts_voice_overrides=voice_map,
        )
        pipeline = RepoToCoursePipeline(config)
        report = pipeline.run()
        print(json.dumps(report, indent=2))
    except Exception as exc:
        logging.getLogger(__name__).exception("Pipeline failed: %s", exc)
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

