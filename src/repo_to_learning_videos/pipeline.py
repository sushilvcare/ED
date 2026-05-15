from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .config import PipelineConfig
from .diagram_generator import generate_sequence, generate_system_flow
from .feature_detection import detect_feature_modules
from .lesson_generator import generate_assignment, generate_lesson_script, generate_quiz
from .repository import collect_repo_snapshot
from .snippet_extractor import extract_snippets
from .video_generator import generate_recording_shotlist, generate_scene_plan, generate_voiceover_script
from .video_renderer import render_module_video

LOGGER = logging.getLogger(__name__)
STYLE_TO_LOCALE = {
    "english-neutral": "en-US",
    "hindi-teacher-simple": "hi-IN",
    "hindi-indian-man": "hi-IN",
    "urdu-female": "ur-PK",
}
COUNTRY_TO_LOCALE = {
    "IN": "hi-IN",
    "PK": "ur-PK",
    "US": "en-US",
    "GB": "en-US",
    "CA": "en-US",
    "AU": "en-US",
}


class RepoToCoursePipeline:
    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

    def run(self) -> dict[str, object]:
        repo_root, cleanup_dir = _materialize_repo(self.config.repo_source)
        LOGGER.info("Running pipeline for repo: %s", repo_root)
        try:
            snapshot = collect_repo_snapshot(repo_root)
            modules = detect_feature_modules(snapshot)
            LOGGER.info("Detected %s modules from %s files", len(modules), len(snapshot.files))
            output = self._write_outputs(repo_root, snapshot, modules)
            return output
        finally:
            if cleanup_dir and cleanup_dir.exists():
                shutil.rmtree(cleanup_dir, ignore_errors=True)

    def _write_outputs(self, repo_root: Path, snapshot, modules) -> dict[str, object]:
        requested_styles = self.config.narration_styles or ["hindi-teacher-simple", "english-neutral"]
        voice_map = self.config.tts_voice_overrides or {}
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (self.config.output_dir / "scripts").mkdir(exist_ok=True)
        (self.config.output_dir / "diagrams").mkdir(exist_ok=True)
        (self.config.output_dir / "snippets").mkdir(exist_ok=True)
        (self.config.output_dir / "quiz").mkdir(exist_ok=True)
        (self.config.output_dir / "assignments").mkdir(exist_ok=True)
        (self.config.output_dir / "videos").mkdir(exist_ok=True)

        modules_json = []
        locale_manifest: dict[str, dict[str, str]] = {}
        for module in modules:
            safe_slug = module.slug.replace("/", "-")
            video_dir = self.config.output_dir / "videos" / safe_slug
            video_dir.mkdir(parents=True, exist_ok=True)
            (self.config.output_dir / "scripts" / f"{safe_slug}.md").write_text(
                generate_lesson_script(module),
                encoding="utf-8",
            )
            (self.config.output_dir / "diagrams" / f"{safe_slug}-sequence.mmd").write_text(
                generate_sequence(module),
                encoding="utf-8",
            )
            (self.config.output_dir / "quiz" / f"{safe_slug}.md").write_text(
                generate_quiz(module),
                encoding="utf-8",
            )
            (self.config.output_dir / "assignments" / f"{safe_slug}.md").write_text(
                generate_assignment(module),
                encoding="utf-8",
            )

            snippets = extract_snippets(repo_root, module, self.config)
            (self.config.output_dir / "snippets" / f"{safe_slug}.json").write_text(
                json.dumps(snippets, indent=2),
                encoding="utf-8",
            )
            video_files: dict[str, str] = {}
            for style in requested_styles:
                locale = STYLE_TO_LOCALE.get(style, style)
                localized_dir = video_dir / locale
                localized_dir.mkdir(parents=True, exist_ok=True)
                voiceover_text = generate_voiceover_script(module, style)
                (localized_dir / "voiceover-script.md").write_text(
                    voiceover_text,
                    encoding="utf-8",
                )
                (localized_dir / "scene-plan.json").write_text(
                    generate_scene_plan(module),
                    encoding="utf-8",
                )
                (localized_dir / "recording-shotlist.md").write_text(
                    generate_recording_shotlist(module),
                    encoding="utf-8",
                )
                video_file = localized_dir / f"{module.slug}.mp4"
                if self.config.generate_videos:
                    try:
                        video_file = render_module_video(
                            module=module,
                            voiceover_markdown=voiceover_text,
                            module_video_dir=localized_dir,
                            voice=voice_map.get(style, "en-US-AndrewNeural"),
                            snippets=snippets,
                            narration_style=style,
                        )
                        LOGGER.info("Generated module video [%s]: %s", style, video_file)
                    except Exception as exc:
                        LOGGER.warning("Video generation failed for %s (%s): %s", module.slug, style, exc)
                if video_file.exists():
                    video_files[locale] = str(video_file)

            locale_manifest[module.slug] = video_files

            modules_json.append(
                {
                    "name": module.name,
                    "slug": module.slug,
                    "difficulty": module.difficulty.value,
                    "description": module.description,
                    "key_paths": [str(path) for path in module.key_paths],
                    "api_routes": [
                        {
                            "method": route.method,
                            "path": route.path,
                            "source_file": str(route.source_file),
                        }
                        for route in module.api_routes
                    ],
                    "db_models": module.db_models,
                    "middleware": module.middleware,
                    "integrations": [
                        {
                            "name": integration.name,
                            "source_file": str(integration.source_file),
                            "evidence": integration.evidence,
                        }
                        for integration in module.integrations
                    ],
                    "videos_by_locale": video_files,
                }
            )

        (self.config.output_dir / "diagrams" / "system-flow.mmd").write_text(
            generate_system_flow(snapshot, modules),
            encoding="utf-8",
        )
        (self.config.output_dir / "course-outline.md").write_text(
            _generate_course_outline(modules_json),
            encoding="utf-8",
        )
        (self.config.output_dir / "videos" / "locale-manifest.json").write_text(
            json.dumps(
                {
                    "country_to_locale": COUNTRY_TO_LOCALE,
                    "style_to_locale": STYLE_TO_LOCALE,
                    "modules": locale_manifest,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        report = {
            "repo_root": str(repo_root),
            "folders_count": len(snapshot.folders),
            "files_count": len(snapshot.files),
            "api_routes_count": len(snapshot.api_routes),
            "db_models_count": len(snapshot.db_models),
            "narration_styles": requested_styles,
            "country_to_locale": COUNTRY_TO_LOCALE,
            "auth_signals": snapshot.auth_signals,
            "deployment_signals": snapshot.deployment_signals,
            "integrations": [
                {
                    "name": integration.name,
                    "source_file": str(integration.source_file),
                }
                for integration in snapshot.integrations
            ],
            "modules": modules_json,
        }
        (self.config.output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report


def _materialize_repo(repo_source: str) -> tuple[Path, Path | None]:
    if _is_remote_repo_source(repo_source):
        temp_dir = Path(tempfile.mkdtemp(prefix="repo2course-"))
        LOGGER.info("Cloning remote repository: %s", repo_source)
        clone_cmd = ["git", "clone", "--depth", "1", repo_source, str(temp_dir)]
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token and "github.com" in repo_source:
            clone_cmd = [
                "git",
                "-c",
                f"http.extraHeader=Authorization: Bearer {github_token}",
                "clone",
                "--depth",
                "1",
                repo_source,
                str(temp_dir),
            ]
        try:
            subprocess.run(
                clone_cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip() or "No stderr output from git clone."
            raise RuntimeError(f"Failed to clone repository: {stderr}") from exc
        return temp_dir, temp_dir
    repo_path = Path(repo_source)
    resolved = repo_path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Repository path does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Repository path must be a directory: {resolved}")
    return resolved, None


def _is_remote_repo_source(repo_source: str) -> bool:
    return (
        repo_source.startswith("http://")
        or repo_source.startswith("https://")
        or repo_source.startswith("ssh://")
        or repo_source.startswith("git@")
    )


def _generate_course_outline(modules_json: list[dict[str, object]]) -> str:
    buckets: dict[str, list[str]] = {"beginner": [], "intermediate": [], "advanced": []}
    for item in modules_json:
        difficulty = str(item.get("difficulty", "intermediate"))
        name = str(item.get("name", "Untitled Module"))
        slug = str(item.get("slug", "module"))
        buckets.setdefault(difficulty, []).append(f"- {name} (`{slug}`)")

    def section(title: str, key: str) -> str:
        entries = "\n".join(buckets.get(key, [])) or "- No modules detected"
        return f"## {title}\n{entries}\n"

    return (
        "# Auto-Generated Course Outline\n\n"
        "Use this sequence for publishing lessons and recording videos.\n\n"
        f"{section('Beginner Track', 'beginner')}\n"
        f"{section('Intermediate Track', 'intermediate')}\n"
        f"{section('Advanced Track', 'advanced')}\n"
        "## Video Production Notes\n"
        "- Each module has assets in `output/videos/<module>/`\n"
        "- Record using `voiceover-script.md` and `recording-shotlist.md`\n"
        "- Export MP4 files and upload to your LMS\n"
    )

