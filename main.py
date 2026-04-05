"""
main.py — DeskFlow FastAPI entry point.

Run:
    python3 main.py
    # or
    uvicorn main:app --reload
"""

import logging
import os
import threading

from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from adapters.fastapi_adapter import router

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    _preload_knowledge_base()
    _preload_model_async()
    yield


app = FastAPI(title="DeskFlow", description="AI-powered IT Helpdesk", lifespan=lifespan)

# Register API routes
app.include_router(router)

# Serve the frontend from public/
app.mount("/static", StaticFiles(directory="public"), name="static")


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


def _preload_model_async() -> None:
    """Load the LLM in a background thread so the server starts immediately."""
    def _load():
        from llm.responder import load_model
        model_path = os.environ.get("MODEL_PATH", None)
        logger.info("Background model load starting (model: %s)", model_path or "LiquidAI/LFM2.5-350M-ONNX")
        load_model(model_path)

    thread = threading.Thread(target=_load, daemon=True, name="model-loader")
    thread.start()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
