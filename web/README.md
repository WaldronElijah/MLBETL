# MLBETL web (Next.js)

Reads game data from the repo’s **FastAPI** app (`GET /api/games`, `GET /api/games/{id}`).

## Local setup

1. Start the API (repo root, with `DATABASE_URL` set), e.g.  
   `PYTHONPATH=src uvicorn mlbetl.api.main:app --reload --host 0.0.0.0 --port 8000`

2. Copy env and install dependencies:

   ```bash
   cp .env.local.example .env.local
   npm install
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000).

`NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000` if unset.

## CORS

The API uses `CORS_ORIGINS` (see repo [`.env.example`](../.env.example)). The default `http://localhost:3000` matches `next dev`. For production, add your deployed site origin (comma-separated).

## Deploy (Vercel)

1. Set project env **`NEXT_PUBLIC_API_URL`** to your public API base URL (no trailing slash), e.g. `https://api.example.com`.

2. On the API host, append your Vercel app URL to **`CORS_ORIGINS`**.

Neon credentials stay on the API only; the browser never uses `DATABASE_URL`.
