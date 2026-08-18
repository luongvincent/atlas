from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.routes.chart import router as chart_router
from api.routes.etfs import router as etfs_router
from api.routes.explain import router as explain_router
from api.routes.onboarding import router as onboarding_router
from api.routes.stats import router as stats_router
from api.routes.tickers import router as tickers_router
from config import get_settings
from core.rate_limit import limiter
from core.security_headers import SecurityHeadersMiddleware

settings = get_settings()

app = FastAPI(title="Atlas Capital", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Order matters: Starlette wraps middleware added *later* around the ones
# added earlier, so the last one added here (CORS) ends up outermost -
# meaning even a 429 from the rate limiter or an error response still gets
# CORS headers, instead of the browser silently blocking it.
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(tickers_router)
app.include_router(explain_router)
app.include_router(onboarding_router)
app.include_router(chart_router)
app.include_router(stats_router)
app.include_router(etfs_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
