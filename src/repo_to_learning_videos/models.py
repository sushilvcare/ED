from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass(slots=True)
class ApiRoute:
    method: str
    path: str
    source_file: Path


@dataclass(slots=True)
class Integration:
    name: str
    source_file: Path
    evidence: str


@dataclass(slots=True)
class FeatureModule:
    name: str
    slug: str
    description: str
    difficulty: Difficulty
    key_paths: list[Path]
    api_routes: list[ApiRoute] = field(default_factory=list)
    db_models: list[str] = field(default_factory=list)
    middleware: list[str] = field(default_factory=list)
    integrations: list[Integration] = field(default_factory=list)


@dataclass(slots=True)
class RepoSnapshot:
    root: Path
    folders: list[Path]
    files: list[Path]
    api_routes: list[ApiRoute]
    db_models: list[str]
    auth_signals: list[str]
    deployment_signals: list[str]
    integrations: list[Integration]

