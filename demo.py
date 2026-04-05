"""
demo.py — DeskFlow terminal demo.

Simulates 5 user messages through the full pipeline:
  detected intent → form ID → context snippet → response

Run without Chainlit:
    python3 demo.py
"""

import logging
import os
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()

logging.basicConfig(level="WARNING")  # Silence info logs for clean demo output

sys.path.insert(0, os.path.dirname(__file__))

from intent.classifier import detect_intent, get_intro_message
from forms.dispatcher import dispatch_form
from rag.retriever import retrieve_context, invalidate_index
from llm.responder import generate_response_template

console = Console()

DEMO_MESSAGES = [
    "My Cisco AnyConnect VPN keeps disconnecting every 10 minutes from home.",
    "I forgot my Microsoft 365 password and my account is locked — it's urgent!",
    "The keyboard on my Dell laptop has stopped working after a Windows update.",
    "I need to request read-only access to the Finance shared drive for my project.",
    "We have a new joiner starting on Monday — need to onboard them with laptop and system setup.",
]


def run_demo():
    console.print(Panel.fit(
        "[bold blue]DeskFlow — AI-powered IT Helpdesk Demo[/bold blue]\n"
        "[dim]Simulating 5 IT support requests through the full pipeline[/dim]",
        border_style="blue",
    ))

    invalidate_index()
    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "./knowledge/runbooks")

    for i, message in enumerate(DEMO_MESSAGES, 1):
        console.print(Rule(f"[bold]Request {i}/{len(DEMO_MESSAGES)}[/bold]"))
        console.print(f"\n[bold yellow]User:[/bold yellow] {message}\n")

        # Step 1: Intent detection
        intent = detect_intent(message)
        intro = get_intro_message(intent)
        console.print(f"[bold green]Detected intent:[/bold green] {intent}")
        console.print(f"[bold green]Intro:[/bold green] {intro}")

        # Step 2: Form dispatch
        form_html = dispatch_form(intent)
        # Extract form ID from HTML
        form_id_start = form_html.find('id="') + 4
        form_id_end = form_html.find('"', form_id_start)
        form_id = form_html[form_id_start:form_id_end]
        console.print(f"[bold green]Form dispatched:[/bold green] {form_id}")

        # Step 3: RAG retrieval (simulate with form result dict)
        form_result = {
            "form_id": form_id,
            "typed_data": {"query": message},
        }
        context = retrieve_context(form_result, top_k=3, knowledge_dir=knowledge_dir)
        context_snippet = context[:200].replace("\n", " ") if context else "(no context)"
        console.print(f"[bold green]Context snippet:[/bold green] {context_snippet}...")

        # Step 4: Template response (no model required for demo)
        response = generate_response_template({"form_id": form_id, "typed_data": {"urgency": "medium"}})
        # Show first 300 chars of response
        preview = response.strip()[:300]
        console.print(Panel(preview + "\n[dim]...[/dim]", title="[bold]Response Preview[/bold]", border_style="cyan"))
        console.print()

    console.print(Panel.fit(
        "[bold green]Demo complete![/bold green]\n"
        "Run [bold]chainlit run main.py[/bold] to start the full interactive chat.",
        border_style="green",
    ))


if __name__ == "__main__":
    run_demo()
