from __future__ import annotations

import re
from pathlib import Path

from .models import ApiRoute, Integration, RepoSnapshot

EXCLUDED_DIRS = {".git", "node_modules", ".next", "dist", "build", ".venv", "__pycache__"}

ROUTE_REGEX = re.compile(
    r"""(?P<method>get|post|put|patch|delete|options|head)\s*\(\s*['"](?P<path>[^'"]+)['"]""",
    re.IGNORECASE,
)
FASTAPI_ROUTE_REGEX = re.compile(
    r"""@(?:router|app)\.(?P<method>get|post|put|patch|delete|options|head)\(\s*['"](?P<path>[^'"]+)['"]""",
    re.IGNORECASE,
)
MODEL_REGEX = re.compile(r"""class\s+(?P<name>[A-Za-z0-9_]+)\s*\((?:db\.)?Model\)""")
MONGOOSE_REGEX = re.compile(r"""mongoose\.model\(\s*['"](?P<name>[A-Za-z0-9_]+)['"]""")

INTEGRATION_PATTERNS: dict[str, re.Pattern[str]] = {
    "Stripe": re.compile(r"\bstripe\b", re.IGNORECASE),
    "Razorpay": re.compile(r"\brazorpay\b", re.IGNORECASE),
    "PayPal": re.compile(r"\bpaypal\b", re.IGNORECASE),
    "Twilio": re.compile(r"\btwilio\b", re.IGNORECASE),
    "SendGrid": re.compile(r"\bsendgrid\b", re.IGNORECASE),
    "AWS": re.compile(r"\baws\b|\bs3\b|\blambda\b", re.IGNORECASE),
    "Redis": re.compile(r"\bredis\b", re.IGNORECASE),
    "Kafka": re.compile(r"\bkafka\b", re.IGNORECASE),
}

AUTH_PATTERNS = [
    re.compile(r"\bjsonwebtoken\b|\bjwt\b", re.IGNORECASE),
    re.compile(r"\bpassport\b", re.IGNORECASE),
    re.compile(r"\boauth\b", re.IGNORECASE),
    re.compile(r"\brefresh[_-]?token\b", re.IGNORECASE),
    re.compile(r"\bnextauth\b", re.IGNORECASE),
]

DEPLOYMENT_FILE_HINTS = {
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "k8s.yaml",
    "kubernetes.yaml",
    "vercel.json",
    "netlify.toml",
    ".github/workflows",
}


def collect_repo_snapshot(repo_root: Path) -> RepoSnapshot:
    folders: list[Path] = []
    files: list[Path] = []
    api_routes: list[ApiRoute] = []
    db_models: list[str] = []
    auth_signals: list[str] = []
    deployment_signals: list[str] = []
    integrations: list[Integration] = []

    for path in repo_root.rglob("*"):
        if _is_excluded(path, repo_root):
            continue
        rel_path = path.relative_to(repo_root)
        if path.is_dir():
            folders.append(rel_path)
            if any(str(rel_path).lower().startswith(hint) for hint in DEPLOYMENT_FILE_HINTS):
                deployment_signals.append(str(rel_path))
            continue

        if not path.is_file():
            continue

        files.append(rel_path)
        if _looks_like_deployment_file(rel_path):
            deployment_signals.append(str(rel_path))

        content = _safe_read_text(path)
        if not content:
            continue

        api_routes.extend(_extract_routes(content, rel_path))
        db_models.extend(_extract_models(content))
        auth_signals.extend(_extract_auth_signals(content, rel_path))
        integrations.extend(_extract_integrations(content, rel_path))

    db_models = sorted(set(db_models))
    auth_signals = sorted(set(auth_signals))
    deployment_signals = sorted(set(deployment_signals))
    integrations = _dedupe_integrations(integrations)

    return RepoSnapshot(
        root=repo_root,
        folders=sorted(folders),
        files=sorted(files),
        api_routes=api_routes,
        db_models=db_models,
        auth_signals=auth_signals,
        deployment_signals=deployment_signals,
        integrations=integrations,
    )


def _is_excluded(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root)
    return any(part in EXCLUDED_DIRS for part in rel.parts)


def _looks_like_deployment_file(rel_path: Path) -> bool:
    lowered = str(rel_path).lower()
    return (
        rel_path.name.lower() in DEPLOYMENT_FILE_HINTS
        or lowered.endswith(".tf")
        or lowered.endswith("helm/values.yaml")
        or lowered.endswith(".github/workflows/ci.yml")
        or lowered.endswith(".github/workflows/deploy.yml")
    )


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""
    except Exception:
        return ""


def _extract_routes(content: str, rel_path: Path) -> list[ApiRoute]:
    routes: list[ApiRoute] = []
    for regex in (ROUTE_REGEX, FASTAPI_ROUTE_REGEX):
        for match in regex.finditer(content):
            routes.append(
                ApiRoute(
                    method=match.group("method").upper(),
                    path=match.group("path"),
                    source_file=rel_path,
                )
            )
    return routes


def _extract_models(content: str) -> list[str]:
    names = [m.group("name") for m in MODEL_REGEX.finditer(content)]
    names.extend(m.group("name") for m in MONGOOSE_REGEX.finditer(content))
    return names


def _extract_auth_signals(content: str, rel_path: Path) -> list[str]:
    matches: list[str] = []
    for pattern in AUTH_PATTERNS:
        if pattern.search(content):
            matches.append(str(rel_path))
            break
    return matches


def _extract_integrations(content: str, rel_path: Path) -> list[Integration]:
    found: list[Integration] = []
    for name, pattern in INTEGRATION_PATTERNS.items():
        if pattern.search(content):
            found.append(Integration(name=name, source_file=rel_path, evidence="keyword-match"))
    return found


def _dedupe_integrations(items: list[Integration]) -> list[Integration]:
    seen: set[tuple[str, Path]] = set()
    result: list[Integration] = []
    for item in items:
        key = (item.name, item.source_file)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result

