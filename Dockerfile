# ---- Builder stage: resolve and install dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage: minimal image with only what's needed to run the app ----
FROM python:3.11-slim AS runtime

# Non-root user the app runs as
RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /app

# Installed dependencies from the builder stage
COPY --from=builder /install /usr/local

# Application source only (no tests, frontend, docs, or env files)
COPY app ./app

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
