import time
from urllib.parse import urlencode

import httpx
import jwt as pyjwt
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..schemas import TokenOut
from ..security import create_access_token


class GoogleTokenIn(BaseModel):
    access_token: str

router = APIRouter(prefix="/auth", tags=["oauth"])

oauth = OAuth()
_providers: set[str] = set()

if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url=(
            "https://accounts.google.com/.well-known/openid-configuration"
        ),
        client_kwargs={"scope": "openid email profile"},
    )
    _providers.add("google")

if (
    settings.apple_client_id
    and settings.apple_team_id
    and settings.apple_key_id
    and settings.apple_private_key
):
    oauth.register(
        name="apple",
        client_id=settings.apple_client_id,
        authorize_url="https://appleid.apple.com/auth/authorize",
        access_token_url="https://appleid.apple.com/auth/token",
        client_kwargs={"scope": "name email", "response_mode": "form_post"},
    )
    _providers.add("apple")


def _apple_client_secret() -> str:
    now = int(time.time())
    payload = {
        "iss": settings.apple_team_id,
        "iat": now,
        "exp": now + 60 * 60 * 24 * 30,  # 30 days (Apple max is 6 months)
        "aud": "https://appleid.apple.com",
        "sub": settings.apple_client_id,
    }
    return pyjwt.encode(
        payload,
        settings.apple_private_key,
        algorithm="ES256",
        headers={"kid": settings.apple_key_id},
    )


def _redirect_with_token(token: str) -> RedirectResponse:
    qs = urlencode({"token": token})
    return RedirectResponse(f"{settings.frontend_url}/auth/callback?{qs}")


def _redirect_with_error(message: str) -> RedirectResponse:
    qs = urlencode({"error": message})
    return RedirectResponse(f"{settings.frontend_url}/auth/callback?{qs}")


def _upsert_oauth_user(
    db: Session,
    *,
    provider: str,
    provider_sub: str,
    email: str | None,
    name: str | None,
) -> User:
    field = "google_id" if provider == "google" else "apple_id"

    user = db.scalar(select(User).where(getattr(User, field) == provider_sub))
    if not user and email:
        user = db.scalar(select(User).where(User.email == email))
        if user:
            setattr(user, field, provider_sub)
    if not user:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{provider} did not return an email; cannot create account",
            )
        # Accounts are company-based, but OAuth doesn't surface a company.
        # Seed company_name with the person's name (or email handle) so the
        # NOT NULL constraint is satisfied; the user can edit it in Settings.
        seed_company = name or email.split("@")[0]
        user = User(
            email=email,
            contact_name=name,
            company_name=seed_company,
            **{field: provider_sub},
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


@router.get("/providers")
def providers() -> dict[str, list[str]]:
    return {"providers": sorted(_providers)}


# ---------- Google ----------


@router.get("/google/login")
async def google_login(request: Request):
    if "google" not in _providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token_data = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return _redirect_with_error(str(e))

    info = token_data.get("userinfo")
    if not info:
        info = await oauth.google.userinfo(token=token_data)

    user = _upsert_oauth_user(
        db,
        provider="google",
        provider_sub=info["sub"],
        email=info.get("email"),
        name=info.get("name"),
    )
    return _redirect_with_token(create_access_token(str(user.id)))


@router.post("/google/token", response_model=TokenOut)
async def google_token(
    payload: GoogleTokenIn, db: Session = Depends(get_db)
) -> TokenOut:
    """Exchange a Google OAuth access token (obtained client-side via
    @react-oauth/google) for our own JWT.

    Two-step verification with Google:
      1. /tokeninfo  -> confirm the token is valid AND was issued to OUR
         client ID (prevents tokens from other apps being replayed here).
      2. /userinfo   -> pull the profile (sub/email/name)."""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on the server",
        )

    async with httpx.AsyncClient(timeout=10) as client:
        tokeninfo = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"access_token": payload.access_token},
        )
        if tokeninfo.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google access token",
            )
        if tokeninfo.json().get("aud") != settings.google_client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google token was not issued to this application",
            )

        userinfo = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {payload.access_token}"},
        )
    if userinfo.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not fetch Google profile",
        )

    info = userinfo.json()
    user = _upsert_oauth_user(
        db,
        provider="google",
        provider_sub=info["sub"],
        email=info.get("email"),
        name=info.get("name"),
    )
    return TokenOut(access_token=create_access_token(str(user.id)))


# ---------- Apple ----------


@router.get("/apple/login")
async def apple_login(request: Request):
    if "apple" not in _providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Apple Sign In not configured",
        )
    oauth.apple.client_secret = _apple_client_secret()
    redirect_uri = str(request.url_for("apple_callback"))
    return await oauth.apple.authorize_redirect(request, redirect_uri)


@router.post("/apple/callback", name="apple_callback")
async def apple_callback(request: Request, db: Session = Depends(get_db)):
    oauth.apple.client_secret = _apple_client_secret()
    try:
        token_data = await oauth.apple.authorize_access_token(request)
    except OAuthError as e:
        return _redirect_with_error(str(e))

    id_token = token_data.get("id_token")
    if not id_token:
        return _redirect_with_error("Apple did not return an id_token")

    # Apple's id_token is already validated by Authlib's token exchange; pull claims.
    claims = pyjwt.decode(id_token, options={"verify_signature": False})

    user = _upsert_oauth_user(
        db,
        provider="apple",
        provider_sub=claims["sub"],
        email=claims.get("email"),
        name=None,
    )
    return _redirect_with_token(create_access_token(str(user.id)))
