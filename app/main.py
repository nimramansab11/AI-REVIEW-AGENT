
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .reviewer_agent import run_reviewer


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="ReviewAI",
    description="Multi-Agent AI Content Reviewer powered by LangGraph.",
    version="1.0.0",
)


class ReviewRequest(BaseModel):
    content: str


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/review")
def review(request: ReviewRequest):

    if not request.content.strip():
        return {
            "error": "Please provide content to review."
        }

    result = run_reviewer(request.content)

    return {
        "review": result
    }
