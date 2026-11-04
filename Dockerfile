# dropship-system – product research CLI
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DROPSHIP_DATA_DIR=/app/data \
    DROPSHIP_CONFIG=/app/config/settings.toml

WORKDIR /app
RUN useradd --create-home --uid 1000 dropship

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install . && rm -rf /root/.cache

COPY config ./config
RUN mkdir -p /app/data/cache /app/data/runs /app/data/reports && chown -R dropship:dropship /app

USER dropship
VOLUME ["/app/data"]
ENTRYPOINT ["dropship"]
CMD ["--help"]
