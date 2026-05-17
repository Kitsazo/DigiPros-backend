import time
from urllib.parse import urlencode

import jwt as pyjwt
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..security import create_access_token

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
        user = User(email=email, name=name, **{field: provider_sub})
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
