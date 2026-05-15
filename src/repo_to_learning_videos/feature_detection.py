from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from .models import Difficulty, FeatureModule, RepoSnapshot

FEATURE_HINTS: dict[str, tuple[str, list[str], Difficulty]] = {
    "authentication": ("Authentication", ["auth", "login", "signup", "jwt", "session"], Difficulty.BEGINNER),
    "payment-processing": ("Payment Processing", ["payment", "billing", "invoice", "checkout", "stripe"], Difficulty.INTERMEDIATE),
    "order-lifecycle": ("Order Lifecycle", ["order", "cart", "shipment", "fulfillment"], Difficulty.INTERMEDIATE),
    "webhooks": ("Webhooks", ["webhook", "callback", "event"], Difficulty.INTERMEDIATE),
    "admin-architecture": ("Admin Architecture", ["admin", "dashboard", "rbac", "role"], Difficulty.ADVANCED),
    "notifications": ("Notifications", ["notification", "email", "sms", "push"], Difficulty.BEGINNER),
}


def detect_feature_modules(snapshot: RepoSnapshot) -> list[FeatureModule]:
    path_buckets: dict[str, set[Path]] = defaultdict(set)
    route_buckets: dict[str, list] = defaultdict(list)
    integration_buckets: dict[str, list] = defaultdict(list)

    for rel_path in snapshot.files + snapshot.folders:
        normalized = str(rel_path).lower()
        for slug, (_name, hints, _difficulty) in FEATURE_HINTS.items():
            if any(hint in normalized for hint in hints):
                path_buckets[slug].add(rel_path)

    for route in snapshot.api_routes:
        normalized = f"{route.path} {route.source_file}".lower()
        for slug, (_name, hints, _difficulty) in FEATURE_HINTS.items():
            if any(hint in normalized for hint in hints):
                route_buckets[slug].append(route)

    for integration in snapshot.integrations:
        normalized = f"{integration.name} {integration.source_file}".lower()
        for slug, (_name, hints, _difficulty) in FEATURE_HINTS.items():
            if any(hint in normalized for hint in hints):
                integration_buckets[slug].append(integration)

    modules: list[FeatureModule] = []
    for slug, (name, _hints, difficulty) in FEATURE_HINTS.items():
        paths = sorted(path_buckets.get(slug, []))
        routes = route_buckets.get(slug, [])
        integrations = integration_buckets.get(slug, [])
        if not paths and not routes and not integrations:
            continue

        db_models = _match_models_to_paths(snapshot.db_models, paths)
        middleware = _extract_middleware(paths)
        description = _build_description(name, routes_count=len(routes), model_count=len(db_models))
        modules.append(
            FeatureModule(
                name=name,
                slug=slug,
                description=description,
                difficulty=difficulty,
                key_paths=paths[:18],
                api_routes=routes[:24],
                db_models=db_models,
                middleware=middleware,
                integrations=integrations[:12],
            )
        )

    return modules


def _match_models_to_paths(db_models: list[str], paths: list[Path]) -> list[str]:
    if not db_models:
        return []
    path_text = " ".join(str(path).lower() for path in paths)
    selected = [model for model in db_models if model.lower() in path_text]
    return sorted(set(selected))[:12]


def _extract_middleware(paths: list[Path]) -> list[str]:
    middleware_patterns = [r"middleware", r"guard", r"interceptor", r"policy", r"permission"]
    middleware_hits: list[str] = []
    for path in paths:
        lowered = str(path).lower()
        if any(re.search(pattern, lowered) for pattern in middleware_patterns):
            middleware_hits.append(str(path))
    return sorted(set(middleware_hits))[:12]


def _build_description(name: str, routes_count: int, model_count: int) -> str:
    return (
        f"{name} contains {routes_count} API routes and {model_count} model references. "
        "Use this module to teach request flow, validation, persistence, and production concerns."
    )

