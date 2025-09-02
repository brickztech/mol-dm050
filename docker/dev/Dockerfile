FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN mkdir -p /app/log

WORKDIR /app

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code
ADD backend ./

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

VOLUME /app/log
EXPOSE 80

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
