"""
FastAPI application — client-facing interface for the vertical keyword tool.

Authentication: simple bearer-token login backed by env-var credentials.
  CLIENT_USERNAME  (default: simone)
  CLIENT_PASSWORD  (default: change-me)
  SECRET_KEY       (used to sign session tokens — set a long random string)
"""

import hmac
import os
import secrets
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config.vertical import DEFAULT_CLIENT_PROFILE
from src.crew import run_keyword_research

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_USERNAME = os.environ.get("CLIENT_USERNAME", "simone")
_PASSWORD = os.environ.get("CLIENT_PASSWORD", "change-me")
_SECRET   = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# In-memory token store: token -> expiry timestamp
_TOKENS: dict[str, float] = {}
_TOKEN_TTL = 60 * 60 * 8  # 8 hours

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_token() -> str:
    return secrets.token_urlsafe(48)


def _verify_token(token: str) -> bool:
    exp = _TOKENS.get(token)
    if exp is None:
        return False
    if time.time() > exp:
        _TOKENS.pop(token, None)
        return False
    return True


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Simone Guarracino — Keyword Research Tool")
bearer = HTTPBearer(auto_error=False)


def require_auth(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if creds is None or not _verify_token(creds.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return creds.credentials


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

_STATIC = Path(__file__).parent.parent / "static"

app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return (_STATIC / "index.html").read_text()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int  # seconds


@app.post("/api/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    ok_user = hmac.compare_digest(body.username, _USERNAME)
    ok_pass = hmac.compare_digest(body.password, _PASSWORD)
    if not (ok_user and ok_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = _make_token()
    _TOKENS[token] = time.time() + _TOKEN_TTL
    return LoginResponse(token=token, expires_in=_TOKEN_TTL)


@app.post("/api/logout")
async def logout(token: str = Depends(require_auth)):
    _TOKENS.pop(token, None)
    return {"ok": True}


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@app.get("/api/categories")
async def get_categories(_: str = Depends(require_auth)):
    return {"categories": DEFAULT_CLIENT_PROFILE["categories"]}


# ---------------------------------------------------------------------------
# Keyword research
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    category: str


@app.post("/api/research")
async def research(body: ResearchRequest, _: str = Depends(require_auth)):
    if body.category not in DEFAULT_CLIENT_PROFILE["categories"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown category")

    # Build a focused profile for just this category
    profile = dict(DEFAULT_CLIENT_PROFILE)
    profile = {**DEFAULT_CLIENT_PROFILE, "categories": [body.category]}

    keywords = run_keyword_research(profile)
    return {"keywords": keywords}
