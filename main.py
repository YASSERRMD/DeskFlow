"""
main.py — DeskFlow Chainlit entry point.

Starts the AI-powered IT Helpdesk chat application.
"""

import logging
import os

from dotenv import load_dotenv
import chainlit as cl

from adapters.chainlit_adapter import on_chat_start, on_message

load_dotenv()

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def _preload_knowledge_base() -> None:
    """Pre-warm the TF-IDF index at startup."""
    from rag.retriever import load_knowledge_base, build_index, _INDEX_CACHE
    import rag.retriever as retriever

    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")
    if retriever._INDEX_CACHE is None:
        logger.info("Loading knowledge base from %s", knowledge_dir)
        chunks = load_knowledge_base(knowledge_dir)
        if chunks:
            retriever._INDEX_CACHE = build_index(chunks)
            logger.info("Knowledge base loaded: %d chunks", len(chunks))
        else:
            logger.warning("No documents found in knowledge directory: %s", knowledge_dir)


def _preload_model() -> None:
    """Attempt to load the LLM at startup (non-blocking on failure)."""
    from llm.responder import load_model
    model_path = os.environ.get("MODEL_PATH", "")
    if model_path:
        logger.info("Pre-loading LLM model from %s", model_path)
        load_model(model_path)
    else:
        logger.info("MODEL_PATH not set — will use template fallback for responses")


# Pre-load on startup
_preload_knowledge_base()
_preload_model()

# Wire Chainlit handlers
cl.on_chat_start(on_chat_start)
cl.on_message(on_message)
