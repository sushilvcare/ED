FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --upgrade pip && pip wheel --wheel-dir /wheels .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    REPO_SOURCE=/work/repo \
    OUTPUT_DIR=/work/output \
    MAX_SNIPPETS=4 \
    MAX_LINES=120 \
    LOG_LEVEL=INFO \
    GENERATE_VIDEOS=true \
    NARRATION_STYLES=hindi-teacher-simple,english-neutral \
    TTS_VOICE= \
    TTS_VOICE_MAP=

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends git openssh-client ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --create-home app

COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links /wheels repo-to-learning-videos && rm -rf /wheels

USER app
ENTRYPOINT ["repo2course"]
