"""
adapters/fastapi_adapter.py — FastAPI route handlers for DeskFlow.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from intent.classifier import detect_intent, get_intro_message
from forms.dispatcher import dispatch_form
from rag.retriever import retrieve_context
from llm.responder import generate_response, generate_response_template

logger = logging.getLogger(__name__)

router = APIRouter()


# ------------------------------------------------------------------ #
# Request / Response models                                            #
# ------------------------------------------------------------------ #

class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    intent: str
    intro: str
    form_html: str


class SubmitRequest(BaseModel):
    form_id: str
    data: dict[str, Any]


class SubmitResponse(BaseModel):
    response: str


# ------------------------------------------------------------------ #
# Routes                                                               #
# ------------------------------------------------------------------ #

@router.post("/api/message", response_model=MessageResponse)
async def handle_message(body: MessageRequest) -> MessageResponse:
    """Detect intent from the user message and return the matching form."""
    intent = detect_intent(body.message)
    intro = get_intro_message(intent)
    form_html = dispatch_form(intent)
    logger.info("Intent detected: %s", intent)
    return MessageResponse(intent=intent, intro=intro, form_html=form_html)


@router.post("/api/submit", response_model=SubmitResponse)
async def handle_submit(body: SubmitRequest) -> SubmitResponse:
    """Process a form submission and return an AI-generated resolution."""
    form_result = {"form_id": body.form_id, "typed_data": body.data}

    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")
    context = retrieve_context(form_result, knowledge_dir=knowledge_dir)

    model_path = os.environ.get("MODEL_PATH", None)
    try:
        response = generate_response(form_result, context, model_path=model_path)
    except Exception as exc:
        logger.error("generate_response failed: %s — using template", exc)
        response = generate_response_template(form_result)

    logger.info("Response generated for form: %s", body.form_id)
    return SubmitResponse(response=response)


@router.get("/api/model-status")
async def model_status():
    """Return whether the LLM pipeline is loaded."""
    import llm.responder as responder
    return {"loaded": responder._PIPELINE is not None}
