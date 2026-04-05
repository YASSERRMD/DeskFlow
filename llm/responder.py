"""
llm/responder.py — LFM2.5-350M-ONNX inference via optimum + onnxruntime.

Falls back to a rule-based template response if the model is not loaded.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

MODEL_LOAD_TIMEOUT = 30  # seconds

# In-memory pipeline cache
_PIPELINE: Any = None


# ------------------------------------------------------------------ #
# Function definitions for tool-use / structured reasoning            #
# ------------------------------------------------------------------ #

FUNCTION_DEFINITIONS: list[dict] = [
    {
        "name": "find_similar_incidents",
        "description": "Look up past incidents similar to the current one.",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "Affected service name"},
                "error_type": {"type": "string", "description": "Type of error"},
                "os": {"type": "string", "description": "Operating system"},
                "urgency": {"type": "string", "description": "Incident urgency level"},
            },
            "required": ["service", "error_type"],
        },
    },
    {
        "name": "retrieve_runbook",
        "description": "Retrieve the relevant IT runbook for the issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Issue category"},
                "os": {"type": "string", "description": "Operating system"},
                "error_type": {"type": "string", "description": "Type of error or symptom"},
            },
            "required": ["category"],
        },
    },
    {
        "name": "suggest_root_cause",
        "description": "Suggest the most likely root cause based on symptoms.",
        "parameters": {
            "type": "object",
            "properties": {
                "symptoms": {"type": "string", "description": "Observed symptoms"},
                "category": {"type": "string", "description": "Issue category"},
                "error_message": {"type": "string", "description": "Error message if any"},
            },
            "required": ["symptoms", "category"],
        },
    },
    {
        "name": "suggest_next_steps",
        "description": "Suggest resolution steps for the issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "severity": {"type": "string", "description": "Issue severity"},
                "category": {"type": "string", "description": "Issue category"},
                "affected_scope": {"type": "string", "description": "Who/what is affected"},
            },
            "required": ["severity", "category"],
        },
    },
]


# ------------------------------------------------------------------ #
# Model loading                                                        #
# ------------------------------------------------------------------ #

_HF_MODEL_ID = "LiquidAI/LFM2.5-350M-ONNX"


def load_model(model_path: str | None = None) -> Any:
    """
    Load LFM2.5-350M-ONNX using optimum ORTModelForCausalLM.

    model_path can be:
      - A local directory path (used as-is)
      - A HuggingFace model ID (e.g. "LiquidAI/LFM2.5-350M-ONNX") — auto-downloads
      - None / empty string → defaults to "LiquidAI/LFM2.5-350M-ONNX" from HuggingFace

    Returns a text-generation pipeline or None on failure.
    Caches the pipeline in memory after first successful load.
    """
    global _PIPELINE
    if _PIPELINE is not None:
        return _PIPELINE

    # Resolve model identifier: local path or HuggingFace model ID
    if not model_path:
        model_id = _HF_MODEL_ID
    elif os.path.isdir(model_path):
        model_id = model_path  # local directory
    else:
        model_id = model_path  # treat as HuggingFace repo ID

    start_time = time.time()
    try:
        from optimum.onnxruntime import ORTModelForCausalLM
        from transformers import AutoTokenizer, pipeline

        logger.info("Loading tokenizer from %s", model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id)

        logger.info("Loading ONNX model from %s (may download from HuggingFace)", model_id)
        model = ORTModelForCausalLM.from_pretrained(model_id)

        elapsed = time.time() - start_time
        if elapsed > MODEL_LOAD_TIMEOUT:
            logger.warning("Model load took %.1fs (exceeded %ds timeout)", elapsed, MODEL_LOAD_TIMEOUT)

        _PIPELINE = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=512,
            do_sample=False,
        )
        logger.info("Model loaded successfully in %.1fs", elapsed)
        return _PIPELINE

    except Exception as exc:
        logger.error("Failed to load model '%s': %s — using template fallback", model_id, exc)
        return None


def unload_model() -> None:
    """Clear the cached pipeline (useful for testing)."""
    global _PIPELINE
    _PIPELINE = None


# ------------------------------------------------------------------ #
# Prompt building                                                      #
# ------------------------------------------------------------------ #

_SYSTEM_PROMPTS: dict[str, str] = {
    "vpn_issue": (
        "You are an expert IT support engineer specializing in VPN connectivity issues. "
        "Provide a structured diagnostic response with: a likely root cause, numbered "
        "resolution steps (Windows and macOS where relevant), and an escalation note if urgency is High or Critical. "
        "Use the following runbook context to inform your response:\n\n{context}"
    ),
    "account_issue": (
        "You are an expert IT support engineer specializing in account and authentication issues. "
        "Provide a structured response with: likely cause, numbered steps to resolve "
        "(include admin steps if relevant), and escalation guidance for High/Critical urgency. "
        "Runbook context:\n\n{context}"
    ),
    "hardware_issue": (
        "You are an expert IT support engineer specializing in hardware diagnostics. "
        "Provide a structured response with: likely cause, numbered troubleshooting steps, "
        "and escalation note for hardware replacement if urgency is High or Critical. "
        "Runbook context:\n\n{context}"
    ),
    "software_issue": (
        "You are an expert IT support engineer specializing in software troubleshooting. "
        "Provide a structured response with: likely cause, numbered resolution steps, "
        "and escalation note for business-critical blocking issues. "
        "Runbook context:\n\n{context}"
    ),
    "network_issue": (
        "You are an expert IT network support engineer. "
        "Provide a structured response with: likely cause, numbered diagnostic and resolution steps, "
        "and escalation guidance for widespread or infrastructure-level issues. "
        "Runbook context:\n\n{context}"
    ),
    "email_issue": (
        "You are an expert IT support engineer specializing in Microsoft 365 and email systems. "
        "Provide a structured response with: likely cause, numbered resolution steps, "
        "and escalation guidance if executive communications are affected. "
        "Runbook context:\n\n{context}"
    ),
    "access_request": (
        "You are an expert IT access management engineer. "
        "Provide a structured response with: access request acknowledgment, the approval workflow, "
        "estimated provisioning time, and escalation path for urgent requests. "
        "Runbook context:\n\n{context}"
    ),
    "procurement_request": (
        "You are an IT procurement specialist. "
        "Provide a structured response with: request acknowledgment, next steps in the procurement process, "
        "expected timeline, and any missing information that could delay the request. "
        "Runbook context:\n\n{context}"
    ),
    "onboarding_setup": (
        "You are an IT onboarding specialist. "
        "Provide a structured response with: onboarding checklist confirmation, "
        "timeline for account and device setup, and what the new joiner can expect on day one. "
        "Runbook context:\n\n{context}"
    ),
    "generic_incident": (
        "You are an expert IT support engineer. "
        "Provide a structured response with: likely cause based on the description, "
        "numbered troubleshooting steps, and escalation guidance if urgency is High or Critical. "
        "Runbook context:\n\n{context}"
    ),
}

_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert IT support engineer. Provide a structured, step-by-step response. "
    "Runbook context:\n\n{context}"
)


def build_system_prompt(form_id: str, context: str) -> str:
    """Return a role-specific system prompt with injected runbook context."""
    template = _SYSTEM_PROMPTS.get(form_id, _DEFAULT_SYSTEM_PROMPT)
    # Truncate context to avoid overwhelming the prompt (keep first 1500 chars)
    truncated_context = context[:1500] if context else "No runbook context available."
    return template.format(context=truncated_context)


def form_result_to_prompt(form_result: Any) -> str:
    """Convert a FormResult (or dict) to a human-readable user prompt."""
    if isinstance(form_result, dict):
        form_id = form_result.get("form_id", "unknown")
        typed_data = form_result.get("typed_data", form_result.get("data", {}))
    else:
        form_id = getattr(form_result, "form_id", "unknown")
        typed_data = getattr(form_result, "typed_data", {}) or {}

    lines = [f"Form submitted: {form_id.replace('_', ' ').title()}"]
    for key, value in typed_data.items():
        if value:
            label = key.replace("_", " ").title()
            lines.append(f"- {label}: {value}")

    return "\n".join(lines)


# ------------------------------------------------------------------ #
# Inference                                                            #
# ------------------------------------------------------------------ #

def generate_response(form_result: Any, context: str, model_path: str | None = None) -> str:
    """
    Generate a markdown-formatted resolution response.

    Uses the ONNX pipeline if loaded, otherwise falls back to template response.
    """
    if model_path is None:
        model_path = os.environ.get("MODEL_PATH", None)  # None → HuggingFace default

    pipe = _PIPELINE or load_model(model_path)

    if pipe is None:
        logger.info("Model not loaded — using template fallback")
        return generate_response_template(form_result)

    system_prompt = build_system_prompt(
        getattr(form_result, "form_id", "") if not isinstance(form_result, dict) else form_result.get("form_id", ""),
        context,
    )
    user_prompt = form_result_to_prompt(form_result)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    start = time.time()
    try:
        output = pipe(messages, max_new_tokens=512, return_full_text=False)
        elapsed = time.time() - start
        logger.info("LLM inference completed in %.2fs", elapsed)

        if isinstance(output, list) and output:
            generated = output[0]
            if isinstance(generated, dict):
                return generated.get("generated_text", "").strip()
            return str(generated).strip()
    except Exception as exc:
        logger.error("LLM inference failed: %s — using template fallback", exc)

    return generate_response_template(form_result)


# ------------------------------------------------------------------ #
# Template fallback                                                    #
# ------------------------------------------------------------------ #

_URGENCY_NOTE = {
    "high": "\n\n> **Escalation**: This issue has been marked **High** urgency. If the steps above do not resolve it within 1 hour, please contact the IT helpdesk directly or call the support line.",
    "critical": "\n\n> **Escalation**: This issue has been marked **CRITICAL**. Please contact the IT helpdesk **immediately** or call the emergency support line. Do not wait.",
}

_TEMPLATE_RESPONSES: dict[str, str] = {
    "vpn_issue": """\
## VPN Issue — Suggested Resolution

**Likely cause:** VPN client configuration issue, credential expiry, or network port blocking.

**Steps to resolve:**

1. Verify your internet connection is working (open a browser and visit any site).
2. Restart the VPN client completely (close from system tray, not just the window).
3. Ensure your username and password are correct and not expired.
4. Check that your MFA token is valid — re-sync your authenticator app if needed.
5. Reboot your device and try again.
6. If on Windows, run `ipconfig /flushdns` in an elevated command prompt.
7. Check if your firewall or antivirus is blocking the VPN port (UDP 1194 / TCP 443).
8. Reinstall the VPN client from the IT software portal.
""",
    "account_issue": """\
## Account Issue — Suggested Resolution

**Likely cause:** Account lockout from failed login attempts, expired password, or MFA misconfiguration.

**Steps to resolve:**

1. Wait 15 minutes — most accounts auto-unlock after a lockout period.
2. Verify Caps Lock is off and you are using the correct username format.
3. Attempt a self-service password reset at the IT portal.
4. Re-sync your MFA authenticator app (check that device time is accurate).
5. Contact IT to manually unlock the account if auto-unlock has not worked.
6. If MFA is the issue, IT can provide a Temporary Access Pass (TAP) for immediate access.
""",
    "hardware_issue": """\
## Hardware Issue — Suggested Resolution

**Likely cause:** Driver issue, physical damage, or hardware component failure.

**Steps to resolve:**

1. Power cycle the device completely (hold power button for 10 seconds, then restart).
2. For peripherals (keyboard, mouse): try a different USB port and test on another machine.
3. Check Device Manager for driver errors (yellow exclamation marks).
4. Update the device driver from the manufacturer's website.
5. Run built-in diagnostics (Dell SupportAssist, HP Support Assistant, or Apple Diagnostics).
6. If the device is physically damaged or the issue persists, contact IT for a hardware assessment.
""",
    "software_issue": """\
## Software Issue — Suggested Resolution

**Likely cause:** Corrupt installation, missing dependencies, license expiry, or permissions issue.

**Steps to resolve:**

1. Close the application completely (check the system tray) and reopen.
2. Run the application as Administrator (right-click → Run as administrator).
3. Check for available updates and install them.
4. Reinstall the application: uninstall from Control Panel, delete leftover app data, then reinstall.
5. Verify you have enough disk space (minimum 10 GB free).
6. Check that your software license is still valid via the license portal.
7. Temporarily disable antivirus and retry if the app is being blocked.
""",
    "network_issue": """\
## Network Issue — Suggested Resolution

**Likely cause:** DHCP lease failure, DNS misconfiguration, or physical connectivity issue.

**Steps to resolve:**

1. Check if other devices on the same network are affected (if yes, the issue is network-side).
2. Restart your network adapter: Device Manager → right-click adapter → Disable, then Enable.
3. On Windows: run `ipconfig /release`, then `ipconfig /renew`, then `ipconfig /flushdns`.
4. Try connecting via Ethernet if you are on Wi-Fi.
5. Test DNS: open Command Prompt and run `nslookup google.com`.
6. Reboot your router/switch if you are at home.
7. If in the office, log a ticket with the Network Operations team.
""",
    "email_issue": """\
## Email / Communications Issue — Suggested Resolution

**Likely cause:** Outlook profile corruption, OST file corruption, or M365 service issue.

**Steps to resolve:**

1. Check the Microsoft 365 service health page for known outages.
2. Test Outlook Web Access (OWA) — if OWA works, the issue is with the desktop client.
3. Restart Outlook from the system tray (not just the X button).
4. Run Outlook in Safe Mode: press Win+R → type `outlook.exe /safe` → Enter.
5. Create a new Outlook profile: Control Panel → Mail → Show Profiles → Add.
6. For Teams issues: clear the Teams cache and reinstall.
""",
    "access_request": """\
## Access Request — Next Steps

**Your access request has been received.**

**What happens next:**

1. An approval email will be sent to your manager at the email address provided.
2. Your manager has **48 hours** to approve or decline the request.
3. Once approved, IT will provision access within **1 business day**.
4. You will receive a confirmation email when access has been granted.
5. For urgent access needs, please reply to this ticket with "URGENT" and provide business justification.
""",
    "procurement_request": """\
## Procurement Request — Next Steps

**Your purchase request has been received.**

**What happens next:**

1. An approval request will be sent to your approving manager.
2. Upon manager approval, IT Procurement will raise a Purchase Order (PO).
3. Standard delivery time: **5–10 business days** for in-stock items.
4. You will receive status updates at each stage: Approved → PO Raised → Dispatched → Delivered.
5. Please ensure your department has sufficient budget before the request is approved.
""",
    "onboarding_setup": """\
## Onboarding Setup — What to Expect

**Your onboarding request has been received.**

**Timeline:**

1. **Account creation**: Your M365 account and email will be created 1–2 days before your start date.
2. **Device provisioning**: Your laptop/desktop will be imaged and configured before day one.
3. **Day-one**: IT will walk you through logging in, setting up MFA, and connecting to VPN.
4. **Access**: All requested system access will be provisioned based on your manager's approvals.
5. **Follow-up**: IT will check in with you on day 3 to address any outstanding issues.
""",
    "generic_incident": """\
## IT Incident — Suggested Resolution

**Likely cause:** Based on your description, this may be related to a software, network, or configuration issue.

**Steps to resolve:**

1. Restart the affected application or service.
2. Reboot your device if the issue persists after restarting the application.
3. Check if other users are affected — if so, this may be an infrastructure issue.
4. Note any error messages or codes and include them in your follow-up.
5. Check the IT status page for known incidents.
6. If the issue persists, IT will escalate for further investigation.
""",
}


def generate_response_template(form_result: Any) -> str:
    """
    Return a rule-based template response based on form_id and urgency.

    Used when the ONNX model is not available.
    """
    if isinstance(form_result, dict):
        form_id = form_result.get("form_id", "generic_incident")
        typed_data = form_result.get("typed_data", form_result.get("data", {}))
    else:
        form_id = getattr(form_result, "form_id", "generic_incident")
        typed_data = getattr(form_result, "typed_data", {}) or {}

    response = _TEMPLATE_RESPONSES.get(form_id, _TEMPLATE_RESPONSES["generic_incident"])

    urgency = str(typed_data.get("urgency", "")).lower()
    if urgency in _URGENCY_NOTE:
        response += _URGENCY_NOTE[urgency]

    return response
