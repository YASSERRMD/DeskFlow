"""
adapters/fastapi_adapter.py — FastAPI route handlers for DeskFlow.

Flow:
  POST /api/message  → intent + chat prompts for LLM reply + form HTML (may be empty)
  POST /api/submit   → RAG retrieval → resolution prompts for browser WebGPU
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

from intent.classifier import detect_intent
from forms.dispatcher import dispatch_form
from rag.retriever import retrieve_context
from llm.responder import (
    build_system_prompt, form_result_to_prompt, generate_response_template,
    build_chat_system_prompt, chat_template_response,
)

logger = logging.getLogger(__name__)

router = APIRouter()

_RESOLUTION_LOG: list[dict] = []


# ------------------------------------------------------------------ #
# Models                                                               #
# ------------------------------------------------------------------ #

class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    intent: str
    form_html: str          # empty string when no form is needed
    system_prompt: str      # LLM system prompt for the conversational reply
    user_prompt: str        # the raw user message
    template_response: str  # fallback text if WebGPU unavailable


class SubmitRequest(BaseModel):
    form_id: str
    data: dict[str, Any]


class SubmitResponse(BaseModel):
    ticket_id: str
    request_number: str
    system_prompt: str
    user_prompt: str
    template_response: str


class ResolveRequest(BaseModel):
    ticket_id: str
    request_number: str
    form_id: str
    data: dict[str, Any]
    response: str
    source: str = "webgpu"


class ResolveResponse(BaseModel):
    ticket_id: str
    status: str


# ------------------------------------------------------------------ #
# Routes                                                               #
# ------------------------------------------------------------------ #

@router.post("/api/message", response_model=MessageResponse)
async def handle_message(body: MessageRequest) -> MessageResponse:
    """
    Detect intent, build LLM chat prompts, and return the matching form (if any).
    The browser runs LLM inference first for a conversational reply, then
    injects the form underneath — giving a natural chat-first experience.
    """
    intent    = detect_intent(body.message)
    form_html = dispatch_form(intent)          # "" for greeting / unknown

    system_prompt     = build_chat_system_prompt(intent)
    template_response = chat_template_response(intent, body.message)

    logger.info("Intent: %s | form: %s", intent, "yes" if form_html else "no")
    return MessageResponse(
        intent=intent,
        form_html=form_html,
        system_prompt=system_prompt,
        user_prompt=body.message,
        template_response=template_response,
    )


@router.post("/api/submit", response_model=SubmitResponse)
async def handle_submit(body: SubmitRequest) -> SubmitResponse:
    """RAG retrieval + resolution prompts for browser-side WebGPU inference."""
    ticket_id      = str(uuid.uuid4())
    request_number = f"INC-{random.randint(1000, 9999)}"
    form_result    = {"form_id": body.form_id, "typed_data": body.data}

    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")
    context       = retrieve_context(form_result, knowledge_dir=knowledge_dir)

    system_prompt     = build_system_prompt(body.form_id, context, request_number)
    user_prompt       = form_result_to_prompt(form_result)
    template_response = generate_response_template(form_result, request_number)

    logger.info("Ticket %s (%s) for form %s", ticket_id, request_number, body.form_id)
    return SubmitResponse(
        ticket_id=ticket_id,
        request_number=request_number,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        template_response=template_response,
    )


@router.post("/api/resolve", response_model=ResolveResponse)
async def handle_resolve(body: ResolveRequest) -> ResolveResponse:
    """Log the browser-generated resolution response."""
    _RESOLUTION_LOG.append({
        "ticket_id":      body.ticket_id,
        "request_number": body.request_number,
        "form_id":        body.form_id,
        "data":           body.data,
        "response":       body.response,
        "source":         body.source,
        "resolved_at":    datetime.datetime.utcnow().isoformat() + "Z",
    })
    logger.info("Resolved %s (%s) via %s", body.ticket_id, body.request_number, body.source)
    return ResolveResponse(ticket_id=body.ticket_id, status="logged")


@router.get("/api/resolutions")
async def list_resolutions():
    return {"count": len(_RESOLUTION_LOG), "items": _RESOLUTION_LOG}
