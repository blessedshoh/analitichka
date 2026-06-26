# Deploying the newsletter generator (free)

The whole app (Next.js UI + FastAPI backend + Playwright Chromium for PDF) ships
as **one Docker image** (`./Dockerfile`) serving on one port. The UI is served
same-origin by the backend, so there's nothing else to wire up.

> Because PDF generation runs headless Chromium, the host needs ~1 GB RAM.
> That rules out the tiniest free tiers. The recommended free option below has
> enough memory.

---

## Option A — Hugging Face Spaces (recommended, free, no card)

Free, ~16 GB RAM, builds straight from the Dockerfile.

1. Create a free account at <https://huggingface.co>.
2. **New → Space**. Name it, set **SDK = Docker**, **Blank** template, choose
   Public or Private. Create.
3. Push this repo to the Space (it gives you a git URL), or upload the files.
   The Space auto-builds from the root `Dockerfile`.
4. Make sure the Space serves on port **7860** (the Dockerfile already does).
   If asked, add this to the **top of the Space's `README.md`**:

   ```yaml
   ---
   title: NBU Newsletter
   sdk: docker
   app_port: 7860
   ---
   ```
5. Wait for the build (a few minutes — it installs Chromium). When it's
   "Running", open the Space URL. That's your website.

**Secrets** (optional — the app runs without them): in the Space's
**Settings → Variables and secrets**, add any of `ANTHROPIC_API_KEY`,
`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_STOCK_CHANNEL`, etc. They map
1:1 to `.env.example`.

---

## Option B — Render.com (free web service)

1. Sign up at <https://render.com> and connect your GitHub.
2. **New → Web Service** → pick this repo.
3. Environment **Docker** (it finds the root `Dockerfile`). Instance type
   **Free**. Render sets `$PORT` automatically — the Dockerfile honours it.
4. Create. First build takes a few minutes (Chromium). Open the `.onrender.com`
   URL.

> Render's free instance sleeps after ~15 min idle and has 512 MB RAM, so PDF
> generation can be slow or memory-tight. Fine for light/occasional use; bump
> to a paid instance if it OOMs.

---

## Option C — any Docker host (Fly.io, Cloud Run, a VPS)

```bash
docker build -t nbu-newsletter .
docker run -p 7860:7860 nbu-newsletter
# open http://localhost:7860
```

Pass secrets with `-e ANTHROPIC_API_KEY=… -e TELEGRAM_API_ID=…` or `--env-file .env`.

---

## Notes

- **Data resets:** Design-mode customisations live in `config/layout.json`,
  which is ephemeral on these hosts (resets on rebuild). Commit a tuned
  `layout.json` into the image if you want it to persist.
- **Access control:** these URLs are public. Use a **Private** HF Space, or put
  the service behind the host's auth, if the content is sensitive.
- **Telegram session:** the MTProto session file must be created once
  interactively (`telethon`) and provided to the container; channel history
  isn't reachable without a logged-in session.
