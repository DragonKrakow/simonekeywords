# Vertical Keyword Finder — Simone Guarracino

A small CrewAI pipeline (running on Groq's free, ultra-fast inference API)
that researches, translates, clusters and prioritizes SEO/search keywords
for a specific niche across multiple markets and platforms. Think of it as
a purpose-built, much lighter alternative to SEMrush for a single client's
vertical — not a general keyword database, but a repeatable research agent
tuned to this brand.

Built for **Simone Guarracino — Luxury Design**: Art Deco / Gatsby-style
luxury home decor and furniture, sold across the UK, Germany, Italy, Spain
and France. The default seed data lives in `src/config/vertical.py` — edit
it (or override it per-request from the dashboard) to reuse this for another
client's vertical.

## How it works

Four CrewAI agents run in sequence, all powered by a Groq-hosted model:

1. **Vertical Strategist** — turns rough categories into tight sub-niches and buyer personas.
2. **Multilingual Keyword Researcher** — generates short- and long-tail keywords per market, in the correct local language (not machine translation).
3. **Platform Strategist** — assigns each keyword the best-fit platform (Google SEO, Google Shopping/Ads, Pinterest, Instagram, TikTok, Etsy).
4. **Keyword Editor** — dedupes, clusters, scores priority 1–5, and outputs clean structured JSON.

The FastAPI backend exposes this as an API and a one-page dashboard where you
can tweak the business description, categories, markets and platforms, run
the crew, review results in a table, and download a CSV.

## 1. Get a free Groq API key

Sign up at [console.groq.com/keys](https://console.groq.com/keys) and
create an API key — Groq's free tier has generous rate limits for models
like the default here, `llama-3.3-70b-versatile`. Check
[console.groq.com/docs/models](https://console.groq.com/docs/models) for
the current model list and limits.

## 2. Run it locally

```bash
git clone <your-repo-url>
cd simone-guarracino-keywords
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste your GROQ_API_KEY

uvicorn src.main:app --reload
```

Open http://localhost:8000 — the form is pre-filled with the client's
default profile. Click **Run keyword research**, wait ~30–90 seconds, review
the table, download the CSV.

## 3. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: vertical keyword finder"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

`.env` is git-ignored by default, so your API key never gets committed.

## 4. Deploy to Render (free tier)

This repo includes a `render.yaml` blueprint, so deployment is mostly automatic:

1. Push the repo to GitHub (step 3).
2. In Render, click **New → Blueprint**, connect the repo, and Render will read `render.yaml`.
3. When prompted, paste your `GROQ_API_KEY` as the environment variable (marked `sync: false` so it isn't stored in the repo).
4. Deploy. Render will run `pip install -r requirements.txt` then `uvicorn src.main:app --host 0.0.0.0 --port $PORT`.

Render's free web service tier sleeps after inactivity and wakes on the next
request (a ~30s cold start) — fine for an internal research tool used a few
times a week. Upgrade the plan in `render.yaml` if you need it always warm.

## Notes and limitations

- This is a keyword *ideation and clustering* tool, not a search-volume or
  ranking-data tool — the model doesn't have live Google Keyword Planner
  data, so treat volumes/competition as unknown and pair this with Google
  Search Console or Google Ads' free Keyword Planner for actual volume
  numbers.
- Runs are synchronous — one request blocks until the crew finishes. Fine
  for occasional manual research; if this becomes a daily habit, worth
  adding a background job queue instead.
- Edit `src/config/vertical.py` any time the client's category list or
  target markets change; the dashboard form always starts from this file.
