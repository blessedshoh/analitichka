# Single-container build: Next.js UI (static export) served same-origin by the
# FastAPI backend, with Playwright Chromium for PDF rendering. One image, one
# port — suitable for Hugging Face Spaces (Docker), Render, Fly, Cloud Run, etc.

# ---- Stage 1: build the frontend as a static export -------------------------
FROM node:22-slim AS ui
WORKDIR /ui
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
# Empty API base => the SPA calls the API on its own origin (same container).
ENV BUILD_STATIC=1 NEXT_PUBLIC_API_BASE="" NEXT_TELEMETRY_DISABLED=1
RUN npm run build      # produces /ui/out

# ---- Stage 2: backend + Chromium, serving the UI ----------------------------
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install chromium

COPY backend/ ./
# Drop the built UI where main.py auto-mounts it (backend/static).
COPY --from=ui /ui/out ./static

# Hugging Face Spaces routes to 7860; override PORT elsewhere if needed.
ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
