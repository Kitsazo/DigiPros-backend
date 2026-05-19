from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .database import init_db
from .routers import analytics, auth, businesses, oauth, quotes, services, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="DigiPros API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.include_router(auth.router)
app.include_router(oauth.router)
app.include_router(users.router)
app.include_router(businesses.router)
app.include_router(services.router)
app.include_router(quotes.router)
app.include_router(analytics.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
