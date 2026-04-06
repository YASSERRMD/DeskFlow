"""
main.py — DeskFlow FastAPI entry point.

Run:
    python3 main.py
    # or
    uvicorn main:app --reload
"""

import logging
import os

from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

from adapters.fastapi_adapter import router


class COOPCOEPMiddleware(BaseHTTPMiddleware):
    """
    Add Cross-Origin-Opener-Policy and Cross-Origin-Embedder-Policy headers to
    every response.  These are required for SharedArrayBuffer, which
    onnxruntime-web needs when running the LLM on WebGPU in the browser.
    (Same headers that barq-web-rag's Vite dev server sets.)
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"
        return response

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _preload_knowledge_base()
    yield


app = FastAPI(title="DeskFlow", description="AI-powered IT Helpdesk", lifespan=lifespan)
app.add_middleware(COOPCOEPMiddleware)

# Register API routes
app.include_router(router)

# Serve the original FastAPI frontend from public/
app.mount("/static", StaticFiles(directory="public"), name="static")

# Serve the standalone frontend-only app from deskflow-web/
app.mount("/web", StaticFiles(directory="deskflow-web", html=True), name="deskflow-web")


@app.get("/", response_class=FileResponse)
async def serve_ui():
    return FileResponse("public/index.html")


def _preload_knowledge_base() -> None:
    """Pre-warm the TF-IDF index."""
    from rag.retriever import load_knowledge_base, build_index
    import rag.retriever as retriever

    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")
    if retriever._INDEX_CACHE is None:
        logger.info("Loading knowledge base from %s", knowledge_dir)
        chunks = load_knowledge_base(knowledge_dir)
        if chunks:
            retriever._INDEX_CACHE = build_index(chunks)
            logger.info("Knowledge base ready: %d chunks indexed", len(chunks))
        else:
            logger.warning("No documents found in: %s", knowledge_dir)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
