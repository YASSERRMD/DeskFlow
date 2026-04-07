"""
adapters/chainlit_adapter.py — Chainlit event handlers for DeskFlow.

Wires together: intent detection → form dispatch → RAG retrieval → LLM response.
"""

from __future__ import annotations

import logging
import os

import chainlit as cl
from barq_chat_form import is_barq_message, parse

from intent.classifier import detect_intent, get_intro_message
from forms.dispatcher import dispatch_form
from rag.retriever import retrieve_context
from llm.responder import generate_response

logger = logging.getLogger(__name__)


async def on_chat_start() -> None:
    """Initialize the chat session."""
    cl.user_session.set("intent_detected", False)
    cl.user_session.set("form_submitted", False)

    await cl.Message(
        content=(
            "Welcome to DeskFlow 👋 How can I help you today? "
            "Describe your IT issue."
        )
    ).send()


async def on_message(message: cl.Message) -> None:
    """Handle incoming chat messages."""
    content = message.content or ""

    if is_barq_message(content):
        await _handle_form_submission(content)
    else:
        await _handle_user_message(content)


async def _handle_form_submission(content: str) -> None:
    """Parse a barq submission, retrieve context, and generate a response."""
    form_result = parse(content)
    if form_result is None:
        logger.warning("Failed to parse barq message")
        await cl.Message(
            content="Sorry, I couldn't read your form submission. Please try again."
        ).send()
        return

    cl.user_session.set("form_submitted", True)
    logger.info("Form submitted: %s", form_result.form_id)

    # Retrieve RAG context
    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")
    context = retrieve_context(form_result, knowledge_dir=knowledge_dir)

    # Generate response
    model_path = os.environ.get("MODEL_PATH", "")
    async with cl.Step(name="Generating response...") as step:
        response = generate_response(form_result, context, model_path=model_path)
        step.output = "Done"

    await cl.Message(content=response).send()

    # Show completion status
    await cl.Message(
        content="✅ Issue logged. A ticket has been created. Our team will follow up if further action is needed."
    ).send()


async def _handle_user_message(content: str) -> None:
    """Detect intent, show intro, and dispatch the appropriate form."""
    intent = detect_intent(content)
    intro = get_intro_message(intent)
    form_html = dispatch_form(intent)

    logger.info("Intent detected: %s", intent)
    cl.user_session.set("intent_detected", True)

    # Send intro message followed by the form
    await cl.Message(content=intro).send()
    await cl.Message(content=form_html).send()
