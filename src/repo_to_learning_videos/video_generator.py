from __future__ import annotations

import json

from .models import FeatureModule


def generate_voiceover_script(module: FeatureModule, style: str = "english-neutral") -> str:
    if style == "hindi-teacher-simple":
        return _generate_hindi_teacher_script(module)
    if style == "hindi-indian-man":
        return _generate_hindi_male_script(module)
    if style == "urdu-female":
        return _generate_urdu_female_script(module)
    return _generate_english_script(module)


def _generate_english_script(module: FeatureModule) -> str:
    key_paths = "\n".join(f"- {path}" for path in module.key_paths[:5]) or "- No key files detected"
    route_summary = ", ".join(f"{route.method} {route.path}" for route in module.api_routes[:4]) or "No routes detected"
    return (
        f"# Voiceover Script: {module.name}\n\n"
        "## Intro (0:00 - 0:20)\n"
        f"In this lesson, we will break down the {module.name} module and understand how it behaves in production systems.\n\n"
        "## Problem Context (0:20 - 1:10)\n"
        f"{module.name} exists to solve a concrete workflow and reduce business friction through reliable API and service boundaries.\n\n"
        "## Request Flow Walkthrough (1:10 - 2:40)\n"
        f"Detected API flow touchpoints: {route_summary}\n"
        "Explain the request entry point, validation strategy, service orchestration, and final response mapping.\n\n"
        "## Code Tour (2:40 - 4:20)\n"
        "Walk through these focused files:\n"
        f"{key_paths}\n\n"
        "## Edge Cases + Production Notes (4:20 - 5:20)\n"
        "Cover retry behavior, idempotency, validation failures, and external dependency timeouts.\n\n"
        "## Interview Drill (5:20 - 6:00)\n"
        "Ask one design question, one debugging question, and one scalability question based on this module.\n"
    )


def _generate_hindi_male_script(module: FeatureModule) -> str:
    key_paths = "\n".join(f"- {path}" for path in module.key_paths[:5]) or "- Koi key file detect nahi hui"
    route_summary = ", ".join(f"{route.method} {route.path}" for route in module.api_routes[:4]) or "Koi route detect nahi hua"
    return (
        f"# Voiceover Script: {module.name}\n\n"
        "## Intro (0:00 - 0:20)\n"
        f"Namaste doston, aaj hum {module.name} module ka deep practical breakdown karenge.\n\n"
        "## Problem Context (0:20 - 1:10)\n"
        f"Yeh module real product workflow ko reliable tarike se handle karta hai, jisse business flow smooth rehta hai.\n\n"
        "## Request Flow Walkthrough (1:10 - 2:40)\n"
        f"Detected API touchpoints: {route_summary}\n"
        "Request router pe aata hai, validation hoti hai, phir service layer logic execute karti hai, aur final response client ko return hota hai.\n\n"
        "## Code Tour (2:40 - 4:20)\n"
        "Ab in focused files ka walkthrough karte hain:\n"
        f"{key_paths}\n\n"
        "## Edge Cases + Production Notes (4:20 - 5:20)\n"
        "Duplicate requests, timeout handling, aur idempotency strategy production me bahut important hoti hai.\n\n"
        "## Interview Drill (5:20 - 6:00)\n"
        "Socho: validation middleware me kya hona chahiye, service me kya, aur scaling ke time kaunsi metrics track karni chahiye.\n"
    )


def _generate_hindi_teacher_script(module: FeatureModule) -> str:
    key_paths = "\n".join(f"- {path}" for path in module.key_paths[:5]) or "- Koi key file detect nahi hui"
    route_summary = ", ".join(f"{route.method} {route.path}" for route in module.api_routes[:4]) or "Koi route detect nahi hua"
    return (
        f"# Voiceover Script: {module.name}\n\n"
        "## Intro (0:00 - 0:20)\n"
        f"Namaste, aaj hum {module.name} ko bilkul basic Hindi me samjhenge, jaise class me teacher board pe samjhata hai.\n\n"
        "## Problem Context (0:20 - 1:10)\n"
        f"Is module ka kaam hai system ka ek important feature stable tarike se chalana, taaki user ko sahi response mile.\n\n"
        "## Request Flow Walkthrough (1:10 - 2:40)\n"
        f"Detected API touchpoints: {route_summary}\n"
        "Step 1 request aati hai, step 2 validation hoti hai, step 3 business logic chalta hai, step 4 response return hota hai.\n\n"
        "## Code Tour (2:40 - 4:20)\n"
        "Ab dashboard par ek ek line code dekhenge:\n"
        f"{key_paths}\n\n"
        "## Edge Cases + Production Notes (4:20 - 5:20)\n"
        "Agar data galat ho, service down ho, ya duplicate request aaye, to system ko safe tareeke se handle karna chahiye.\n\n"
        "## Interview Drill (5:20 - 6:00)\n"
        "Interview me explain karo: ye line kya karti hai, kyun likhi hai, aur agar hata dein to kya risk hoga.\n"
    )


def _generate_urdu_female_script(module: FeatureModule) -> str:
    key_paths = "\n".join(f"- {path}" for path in module.key_paths[:5]) or "- Koi key file detect nahin hui"
    route_summary = ", ".join(f"{route.method} {route.path}" for route in module.api_routes[:4]) or "Koi route detect nahin hua"
    return (
        f"# Voiceover Script: {module.name}\n\n"
        "## Intro (0:00 - 0:20)\n"
        f"Assalam o alaikum, aaj hum {module.name} module ko practical andaaz mein samjhen ge.\n\n"
        "## Problem Context (0:20 - 1:10)\n"
        f"Yeh module product workflow ko stable banata hai aur business process ko behtar karta hai.\n\n"
        "## Request Flow Walkthrough (1:10 - 2:40)\n"
        f"Detected API touchpoints: {route_summary}\n"
        "Request router par aata hai, phir validation aur service logic ke baad final response return hota hai.\n\n"
        "## Code Tour (2:40 - 4:20)\n"
        "In key files par focus karein:\n"
        f"{key_paths}\n\n"
        "## Edge Cases + Production Notes (4:20 - 5:20)\n"
        "Retry strategy, timeout handling, aur duplicate actions se bachna production quality ke liye zaroori hai.\n\n"
        "## Interview Drill (5:20 - 6:00)\n"
        "Sochiye: agar dependency fail ho jaye to fallback design kaise banayenge?\n"
    )


def generate_scene_plan(module: FeatureModule) -> str:
    scenes = [
        {
            "scene": 1,
            "title": "Problem Overview",
            "visual": "Whiteboard or slide with module objective",
            "duration_sec": 20,
            "narration_goal": f"Define why {module.name} matters.",
        },
        {
            "scene": 2,
            "title": "Architecture Flow",
            "visual": "Mermaid sequence diagram on screen",
            "duration_sec": 90,
            "narration_goal": "Explain request lifecycle across layers.",
        },
        {
            "scene": 3,
            "title": "Code Walkthrough",
            "visual": "Editor walkthrough of key files",
            "duration_sec": 120,
            "narration_goal": "Map code to runtime behavior.",
        },
        {
            "scene": 4,
            "title": "Production Pitfalls",
            "visual": "Checklist slide (errors, race, observability)",
            "duration_sec": 60,
            "narration_goal": "Teach hardening and reliability strategy.",
        },
        {
            "scene": 5,
            "title": "Interview Questions",
            "visual": "Q&A card",
            "duration_sec": 30,
            "narration_goal": "Reinforce concepts with interview framing.",
        },
    ]
    return json.dumps({"module": module.name, "slug": module.slug, "scenes": scenes}, indent=2)


def generate_recording_shotlist(module: FeatureModule) -> str:
    return (
        f"# Recording Shotlist: {module.name}\n\n"
        "- [ ] Open `output/diagrams/{slug}-sequence.mmd` and keep it full screen\n"
        "- [ ] Open `output/scripts/{slug}.md` for narration cues\n"
        "- [ ] Open `output/snippets/{slug}.json` for focused code excerpts\n"
        "- [ ] Record 1080p, 30fps, clear microphone input\n"
        "- [ ] Keep each scene under 90 seconds where possible\n"
        "- [ ] Export final MP4 as `{slug}.mp4`\n"
    ).format(slug=module.slug)

