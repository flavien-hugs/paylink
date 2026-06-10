FROM ghcr.io/flavien-hugs/python-poetry-base:latest

# Link the published image to its source repository (GHCR auto-connects the package).
LABEL org.opencontainers.image.source="https://github.com/flavien-hugs/paylink" \
      org.opencontainers.image.title="paylink-backend" \
      org.opencontainers.image.description="PayLink — multi-entity Kkiapay payment platform backend (FastAPI, hexagonal)"

WORKDIR /app

ENV POETRY_VIRTUALENVS_CREATE=false \
    APP_ENTRYPOINT=src.main:app

USER root

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --no-interaction

USER appuser

COPY --chown=appuser:appuser . .

CMD ["./docker-entrypoint.sh"]
