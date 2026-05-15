# Repo -> Learning Videos Pipeline

Convert a repository into teachable learning assets:

- Detected feature modules (`auth`, `payments`, `orders`, `webhooks`, `admin`, `notifications`)
- Architecture diagrams (Mermaid flow + sequence)
- Lesson scripts per module
- Curated code snippets per module
- Quizzes and assignments
- AI-generated playable videos per module (`.mp4`) + production kit
- Structured report with APIs, DB model hints, auth signals, integrations, and deployment signals

Platform MVP now includes:

- Mongo-backed backend API for users/courses/orders/enrollments
- Next.js frontend for landing/catalog/checkout/dashboard/admin
- Docker Compose stack for generator + API + web + preview + Mongo

## How it works

1. Parse repository folders/files.
2. Detect APIs, model patterns, auth flow signals, middleware hints, integrations, deployment config.
3. Group findings into standalone teachable modules.
4. Generate teaching artifacts for each module.
5. Emit outputs you can feed to narration/video tools (HeyGen, Synthesia, Descript) and LMS upload jobs.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Production Docker setup

### Build image

```bash
docker build -t repo2course:latest .
```

### Run container directly (local repo mounted)

```bash
docker run --rm ^
  -e REPO_SOURCE=/work/repo ^
  -e OUTPUT_DIR=/work/output ^
  -e LOG_LEVEL=INFO ^
  -e GENERATE_VIDEOS=true ^
  -e NARRATION_STYLES=hindi-teacher-simple,english-neutral ^
  -e TTS_VOICE_MAP=hindi-teacher-simple:hi-IN-MadhurNeural,english-neutral:en-US-AndrewNeural ^
  -v C:\path\to\repo:/work/repo:ro ^
  -v C:\path\to\output:/work/output ^
  repo2course:latest
```

### Run with docker compose

```bash
copy .env.example .env
docker compose up --build
```

Compose now controls both:

- `repo2course` (artifact/video generation)
- `preview` (frontend/static preview server)
- `mongo` (database)
- `platform-api` (backend API)
- `platform-web` (Next.js app)

Preview URL:

- `http://127.0.0.1:4173/frontend/preview/index.html`
- `http://127.0.0.1:3000` (platform web app)
- `http://127.0.0.1:8080/health` (platform API health)

`docker-compose.yml` is production-friendly by default:
- non-root container runtime
- read-only source mount (`:ro`)
- environment-driven runtime options
- deterministic entrypoint (`repo2course`)

## Run

### Local repo

```bash
repo2course --repo "C:\path\to\repo" --output output
```

### GitHub repo URL

```bash
repo2course --repo "https://github.com/org/repo.git" --output output
```

### SSH repo URL

```bash
repo2course --repo "git@github.com:org/repo.git" --output output
```

For Docker + SSH URLs, mount your SSH keys:

```bash
docker run --rm ^
  -e REPO_SOURCE="git@github.com:org/repo.git" ^
  -e OUTPUT_DIR=/work/output ^
  -v C:\Users\<you>\.ssh:/home/app/.ssh:ro ^
  -v C:\path\to\output:/work/output ^
  repo2course:latest
```

You can also set runtime values from environment variables:

- `REPO_SOURCE`
- `OUTPUT_DIR`
- `MAX_SNIPPETS`
- `MAX_LINES`
- `LOG_LEVEL`
- `GITHUB_TOKEN` (optional, required for private GitHub repos)
- `GENERATE_VIDEOS` (`true/false`)
- `NARRATION_STYLES` (comma-separated styles, e.g. `hindi-teacher-simple,english-neutral`)
- `TTS_VOICE` (optional single fallback voice for all styles)
- `TTS_VOICE_MAP` (optional per-style override: `style:voice,style:voice`)
- `APP_JWT_SECRET`
- `APP_MONGO_URL`
- `APP_MONGO_DB`
- `NEXT_PUBLIC_API_BASE_URL`

`hindi-teacher-simple` mode adds code-teaching slides that explain line-by-line "kya" and "kyun".

## Output structure

```text
output/
  report.json
  course-outline.md
  diagrams/
    system-flow.mmd
    <module>-sequence.mmd
  scripts/
    <module>.md
  snippets/
    <module>.json
  quiz/
    <module>.md
  assignments/
    <module>.md
  videos/
    <module>/
      hi-IN/
        <module>.mp4
        voiceover-script.md
        scene-plan.json
        recording-shotlist.md
      en-US/
        <module>.mp4
        voiceover-script.md
        scene-plan.json
        recording-shotlist.md
    locale-manifest.json
```
Generated `.mp4` files are directly playable and can be uploaded to LMS/Udemy workflows.
Use `output/videos/locale-manifest.json` in frontend to map country -> locale -> module video path.

## React frontend component

Drop-in files:

- `frontend/CourseVideoPlayer.tsx`
- `frontend/CourseVideoPlayer.example.tsx`
- `frontend/videoManifest.ts`
- `frontend/nextjs/getCountryCode.ts`
- `frontend/nextjs/CourseVideoPlayerClient.tsx`
- `frontend/nextjs/ModuleVideoPage.example.tsx`

`CourseVideoPlayer` includes:

- manifest fetch (`/videos/locale-manifest.json`)
- loading state
- error state
- country -> locale fallback (`en-US`)
- module video missing state

## Platform backend API (MVP)

Base URL: `http://localhost:8080/api/v1`

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /courses`
- `POST /courses` (admin/creator)
- `PATCH /courses/{course_id}` (admin or owner)
- `POST /orders/create`
- `POST /orders/{order_id}/mark-paid` (admin placeholder before Stripe/Razorpay)
- `GET /orders/my`
- `GET /enrollments/my`
- `GET /admin/summary` (admin)

This is intentionally payment-provider agnostic so Stripe/Razorpay can be plugged in later.

## Next.js App Router ready

Use:

- `getCountryCode()` for server-side geo header detection
- `ModuleVideoPage.example.tsx` as dynamic route page template
- `CourseVideoPlayerClient.tsx` as client wrapper

It supports country-based rendering:

- `IN` -> `hi-IN`
- `US`, `GB`, `CA`, `AU` -> `en-US`
- fallback -> `en-US`

## Example full automation pipeline

```text
GitHub Repo
   ↓
Code parser
   ↓
Feature extraction
   ↓
Script generation + Diagram generation + Snippet extraction
   ↓
Video generation (HeyGen/Synthesia/Descript or screen recording)
   ↓
LMS upload
```

## Notes

- Parsing is heuristic-based and framework-agnostic for portability.
- You can extend feature detection by editing `FEATURE_HINTS` in `src/repo_to_learning_videos/feature_detection.py`.
- You can integrate LLM providers for richer pedagogical scripts in a future step.
- CLI exits non-zero on failure, emits structured logs, and validates local repo paths.

