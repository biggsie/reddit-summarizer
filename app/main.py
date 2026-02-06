from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.api import routes
from app.api.scheduler import start_scheduler
from app.database import init_db
import logging

# Reddit Summarizer - Daily digest with AI summaries

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting scheduler...")
    scheduler = start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()


app = FastAPI(
    title="Reddit Summarizer",
    description="Daily Reddit digest with AI summaries",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["api"])


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os

    # Get port from environment variable (Railway) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
