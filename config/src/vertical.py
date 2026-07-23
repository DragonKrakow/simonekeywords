import csv
import io
import os
import uuid
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from src.config.vertical import DEFAULT_CLIENT_PROFILE  # noqa: E402
from src.crew import run_keyword_research  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Vertical Keyword Finder")


class Market(BaseModel):
    country: str
    language: str
    domain: Optional[str] = None


class ResearchRequest(BaseModel):
    business_description: Optional[str] = None
    categories: Optional[List[str]] = None
    markets: Optional[List[Market]] = None
    platforms: Optional[List[str]] = None


@app.get("/api/default-profile")
def default_profile():
    return DEFAULT_CLIENT_PROFILE


@app.post("/api/research")
def research(req: ResearchRequest):
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set. Add it to your .env (local) or "
                   "environment variables (Render) — get a free key at "
                   "https://console.groq.com/keys",
        )

    profile = dict(DEFAULT_CLIENT_PROFILE)
    if req.business_description:
        profile["business_description"] = req.business_description
    if req.categories:
        profile["categories"] = req.categories
    if req.markets:
        profile["markets"] = [m.dict() for m in req.markets]
    if req.platforms:
        profile["platforms"] = req.platforms

    keywords = run_keyword_research(profile)

    run_id = uuid.uuid4().hex[:10]
    csv_path = OUTPUT_DIR / f"keywords_{run_id}.csv"
    _write_csv(keywords, csv_path)

    return {"run_id": run_id, "count": len(keywords), "keywords": keywords}


@app.get("/api/download/{run_id}")
def download(run_id: str):
    csv_path = OUTPUT_DIR / f"keywords_{run_id}.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    return FileResponse(csv_path, media_type="text/csv", filename=csv_path.name)


def _write_csv(keywords: List[dict], path: Path) -> None:
    fieldnames = ["keyword", "market", "language", "intent", "platform", "cluster", "priority"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in keywords:
            writer.writerow(row)


# Serve the dashboard last so /api/* routes above take precedence
app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")
