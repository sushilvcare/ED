from __future__ import annotations

from pathlib import Path

from .config import PipelineConfig
from .models import FeatureModule


def extract_snippets(repo_root: Path, module: FeatureModule, config: PipelineConfig) -> dict[str, str]:
    snippets: dict[str, str] = {}
    picked = 0
    for rel_path in module.key_paths:
        if picked >= config.max_snippets_per_module:
            break
        absolute = repo_root / rel_path
        if not absolute.is_file():
            continue
        content = _safe_read(absolute)
        if not content:
            continue
        lines = content.splitlines()
        snippet = "\n".join(lines[: config.max_lines_per_snippet])
        snippets[str(rel_path)] = snippet
        picked += 1
    return snippets


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""
    except Exception:
        return ""

