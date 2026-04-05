"""
adapters/fastapi_adapter.py — FastAPI route handlers for DeskFlow.

Flow:
  POST /api/message  → intent detection + form HTML
  POST /api/submit   → RAG retrieval → prompts for browser WebGPU inference
  POST /api/resolve  → browser sends back the generated response for logging
"""

from __future__ import annotations

import logging
import os
import uuid
import random
import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from intent.classifier import detect_intent, get_intro_message
from forms.dispatcher import dispatch_form
from rag.retriever import retrieve_context
from llm.responder import build_system_prompt, form_result_to_prompt, generate_response_template

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory resolution log (form_id → list of resolved tickets)
_RESOLUTION_LOG: list[dict] = []


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
    ticket_id: str          # internal UUID for the resolve call
    request_number: str     # human-readable INC-XXXX shown to the user
    system_prompt: str      # for WebGPU inference in the browser
    user_prompt: str        # for WebGPU inference in the browser
    template_response: str  # fallback when WebGPU is unavailable


class ResolveRequest(BaseModel):
    ticket_id: str
    request_number: str
    form_id: str
    data: dict[str, Any]
    response: str           # the LLM-generated (or template) text from the browser
    source: str = "webgpu"  # "webgpu" | "template"


class ResolveResponse(BaseModel):
    ticket_id: str
    status: str


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
    """
    Run RAG retrieval and build prompts for browser-side WebGPU inference.
    Returns a ticket_id the browser must include in the subsequent /api/resolve call.
    """
    ticket_id = str(uuid.uuid4())
    request_number = f"INC-{random.randint(1000, 9999)}"
    form_result = {"form_id": body.form_id, "typed_data": body.data}

    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")
    context = retrieve_context(form_result, knowledge_dir=knowledge_dir)

    system_prompt = build_system_prompt(body.form_id, context, request_number)
    user_prompt = form_result_to_prompt(form_result)
    template_response = generate_response_template(form_result, request_number)

    logger.info("Ticket %s (%s): prompts built for form %s", ticket_id, request_number, body.form_id)
    return SubmitResponse(
        ticket_id=ticket_id,
        request_number=request_number,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        template_response=template_response,
    )


@router.post("/api/resolve", response_model=ResolveResponse)
async def handle_resolve(body: ResolveRequest) -> ResolveResponse:
    """
    Receive the LLM-generated response from the browser and log the resolved ticket.
    The browser calls this after inference completes (WebGPU or template fallback).
    """
    entry = {
        "ticket_id":      body.ticket_id,
        "request_number": body.request_number,
        "form_id":        body.form_id,
        "data":           body.data,
        "response":       body.response,
        "source":         body.source,
        "resolved_at":    datetime.datetime.utcnow().isoformat() + "Z",
    }
    _RESOLUTION_LOG.append(entry)

    logger.info(
        "Ticket %s resolved via %s (form: %s, response_len: %d chars)",
        body.ticket_id, body.source, body.form_id, len(body.response),
    )
    return ResolveResponse(ticket_id=body.ticket_id, status="logged")


@router.get("/api/resolutions")
async def list_resolutions():
    """Return all logged resolutions (useful for admin/debugging)."""
    return {"count": len(_RESOLUTION_LOG), "items": _RESOLUTION_LOG}
