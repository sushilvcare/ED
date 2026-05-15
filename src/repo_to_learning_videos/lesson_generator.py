from __future__ import annotations

from .models import FeatureModule


def generate_lesson_script(module: FeatureModule) -> str:
    routes = ", ".join(f"{route.method} {route.path}" for route in module.api_routes[:5]) or "No explicit routes detected"
    key_files = "\n".join(f"- `{path}`" for path in module.key_paths[:8]) or "- No dominant files found"
    integration_names = ", ".join(sorted({item.name for item in module.integrations})) or "None detected"

    return (
        f"# Topic: {module.name}\n\n"
        "## 1) What problem does this solve?\n"
        f"{module.name} solves a specific product workflow by coordinating endpoints, business rules, and data persistence.\n\n"
        "## 2) How does request flow work?\n"
        f"Detected routes: {routes}\n"
        "- Entry point reaches router/controller\n"
        "- Service layer executes validations and business logic\n"
        "- Storage/integration calls complete workflow and return response\n\n"
        "## 3) Code walkthrough\n"
        f"{key_files}\n\n"
        "## 4) Edge cases\n"
        "- Invalid payload and schema mismatch\n"
        "- Idempotency/retry behavior for duplicate requests\n"
        "- Timeout or partial failure in downstream systems\n\n"
        "## 5) Production issues\n"
        "- Missing observability around slow endpoints\n"
        "- Race conditions around concurrent updates\n"
        "- Secrets/configuration drift across environments\n\n"
        "## 6) Interview questions\n"
        "- How would you design this module to be idempotent?\n"
        "- Which parts belong in middleware vs service layer?\n"
        "- How do you monitor and alert on failures?\n\n"
        f"### Third-party integrations\n{integration_names}\n"
    )


def generate_quiz(module: FeatureModule) -> str:
    return (
        f"# Quiz: {module.name}\n\n"
        "1. Which layer should own request validation for this module?\n"
        "2. What is one strategy to avoid duplicate side effects?\n"
        "3. Which metric best indicates production degradation here?\n"
        "4. How would you test failure in a downstream integration?\n"
    )


def generate_assignment(module: FeatureModule) -> str:
    return (
        f"# Assignment: {module.name}\n\n"
        "Build a thin vertical slice for this module that includes:\n"
        "- One endpoint and one service method\n"
        "- Input validation + auth checks\n"
        "- Persistence or mocked external integration\n"
        "- Error handling and structured logs\n\n"
        "Stretch goal:\n"
        "- Add retry logic or idempotency key support\n"
    )

