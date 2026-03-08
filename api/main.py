from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import os
from api.routers import player
from api.services.player import compute_player_value
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PPA-DUN API")
API_KEY = os.getenv("API_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # /health, /demo, and OPTIONS requests are exempt from API key check
    if request.url.path == "/health" or request.url.path.startswith("/demo") or request.method == "OPTIONS":
        return await call_next(request)

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing API key"}
        )
    if api_key != API_KEY:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API key"}
        )
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract only the field names that are missing or invalid
    missing_fields = [".".join(str(loc) for loc in err["loc"] if loc != "body") for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"detail": f"Missing fields: {', '.join(missing_fields)}"},
    )


app.include_router(player.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/demo/{player_name}")
def demo(player_name: str):
    # Temporary demo endpoint - will be redesigned in Issue #35
    return {"player_name": player_name, "note": "demo endpoint - Issue #35 pending"}