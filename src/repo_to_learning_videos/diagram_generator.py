from __future__ import annotations

from .models import FeatureModule, RepoSnapshot


def generate_system_flow(snapshot: RepoSnapshot, modules: list[FeatureModule]) -> str:
    module_nodes = "\n".join(
        f'    {m.slug.replace("-", "_")}["{m.name}"]' for m in modules
    )
    module_edges = "\n".join(
        f"    extractor --> {m.slug.replace('-', '_')}" for m in modules
    )
    return (
        "flowchart TD\n"
        "    repo[GitHub Repo / Local Repo] --> parser[Code Parser]\n"
        "    parser --> extractor[Feature Extraction]\n"
        f"{module_nodes}\n"
        f"{module_edges}\n"
        "    extractor --> scripts[Lesson Script Generation]\n"
        "    extractor --> diagrams[Mermaid Diagram Generation]\n"
        "    extractor --> snippets[Code Snippet Extraction]\n"
        "    scripts --> video[Video Generation]\n"
        "    snippets --> quiz[Quizzes + Assignments]\n"
        "    diagrams --> lms[LMS Upload]\n"
        "    video --> lms\n"
        "    quiz --> lms\n"
    )


def generate_sequence(module: FeatureModule) -> str:
    route_label = module.api_routes[0].path if module.api_routes else "/feature-endpoint"
    return (
        "sequenceDiagram\n"
        "    autonumber\n"
        "    participant C as Client\n"
        "    participant R as API Router\n"
        "    participant S as Service Layer\n"
        "    participant D as Database\n"
        "    participant E as External Integrations\n"
        f"    C->>R: Request {route_label}\n"
        "    R->>S: Validate + authorize\n"
        "    S->>D: Read/Write domain data\n"
        "    S->>E: Optional third-party call\n"
        "    E-->>S: Callback/result\n"
        "    S-->>R: Normalized response\n"
        "    R-->>C: HTTP response\n"
    )

