"""
llm/responder.py — Prompt builders and template fallback for DeskFlow.

LLM inference runs browser-side via WebGPU using @huggingface/transformers.
This module provides system/user prompt construction and a rule-based fallback
that is returned when WebGPU is unavailable in the client browser.
"""

from __future__ import annotations

from typing import Any


# ------------------------------------------------------------------ #
# System prompts per form type                                         #
# ------------------------------------------------------------------ #

_SYSTEM_PROMPTS: dict[str, str] = {
    "vpn_issue": (
        "You are an expert IT support engineer specialising in VPN connectivity. "
        "Reply with: 1) Likely cause  2) Numbered resolution steps (Windows and macOS) "
        "3) Escalation note if urgency is High or Critical.\n\nRunbook context:\n{context}"
    ),
    "account_issue": (
        "You are an IT support engineer specialising in account and authentication issues. "
        "Reply with: 1) Likely cause  2) Numbered steps to resolve "
        "3) Escalation guidance for High/Critical urgency.\n\nRunbook context:\n{context}"
    ),
    "hardware_issue": (
        "You are an IT hardware support engineer. "
        "Reply with: 1) Likely cause  2) Numbered troubleshooting steps "
        "3) Escalation note if replacement is needed.\n\nRunbook context:\n{context}"
    ),
    "software_issue": (
        "You are an IT software support engineer. "
        "Reply with: 1) Likely cause  2) Numbered resolution steps "
        "3) Escalation note for business-critical issues.\n\nRunbook context:\n{context}"
    ),
    "network_issue": (
        "You are an IT network support engineer. "
        "Reply with: 1) Likely cause  2) Numbered diagnostic and resolution steps "
        "3) Escalation guidance.\n\nRunbook context:\n{context}"
    ),
    "email_issue": (
        "You are an M365 and email support engineer. "
        "Reply with: 1) Likely cause  2) Numbered resolution steps "
        "3) Escalation guidance.\n\nRunbook context:\n{context}"
    ),
    "access_request": (
        "You are an IT access management engineer. "
        "Reply with: 1) Request acknowledgment  2) Approval workflow steps "
        "3) Estimated provisioning time.\n\nRunbook context:\n{context}"
    ),
    "procurement_request": (
        "You are an IT procurement specialist. "
        "Reply with: 1) Request acknowledgment  2) Next steps in procurement process "
        "3) Expected timeline.\n\nRunbook context:\n{context}"
    ),
    "onboarding_setup": (
        "You are an IT onboarding specialist. "
        "Reply with: 1) Onboarding checklist  2) Timeline for setup "
        "3) What to expect on day one.\n\nRunbook context:\n{context}"
    ),
    "generic_incident": (
        "You are an IT support engineer. "
        "Reply with: 1) Likely cause  2) Numbered troubleshooting steps "
        "3) Escalation guidance for High/Critical urgency.\n\nRunbook context:\n{context}"
    ),
}


def build_system_prompt(form_id: str, context: str) -> str:
    """Return the system prompt for the given form type, with RAG context embedded."""
    template = _SYSTEM_PROMPTS.get(form_id, _SYSTEM_PROMPTS["generic_incident"])
    return template.format(context=context[:1500] if context else "No context available.")


def form_result_to_prompt(form_result: Any) -> str:
    """Convert a form submission dict / object into a plain-text user prompt."""
    if isinstance(form_result, dict):
        form_id = form_result.get("form_id", "unknown")
        typed_data = form_result.get("typed_data", form_result.get("data", {}))
    else:
        form_id = getattr(form_result, "form_id", "unknown")
        typed_data = getattr(form_result, "typed_data", {}) or {}

    lines = [f"IT Support Request: {form_id.replace('_', ' ').title()}"]
    for k, v in typed_data.items():
        if v:
            lines.append(f"- {k.replace('_', ' ').title()}: {v}")
    return "\n".join(lines)


# ------------------------------------------------------------------ #
# Template fallback (used when browser WebGPU is unavailable)         #
# ------------------------------------------------------------------ #

_URGENCY_NOTE = {
    "high": "\n\n> **Escalation**: Marked **High** urgency. If unresolved within 1 hour, contact the IT helpdesk directly.",
    "critical": "\n\n> **Escalation**: Marked **CRITICAL**. Contact the IT helpdesk **immediately** or call the emergency support line.",
}

_TEMPLATE_RESPONSES: dict[str, str] = {
    "vpn_issue": """\
## VPN Issue — Suggested Resolution

**Likely cause:** VPN client configuration issue, credential expiry, or network port blocking.

**Steps to resolve:**

1. Verify your internet connection is working (open a browser and visit any site).
2. Restart the VPN client completely (close from system tray, not just the window).
3. Ensure your username and password are correct and not expired.
4. Re-sync your MFA authenticator app — check device clock is accurate.
5. Reboot your device and try again.
6. On Windows: run `ipconfig /flushdns` in an elevated command prompt.
7. Check that your firewall or antivirus is not blocking the VPN port (UDP 1194 / TCP 443).
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
2. For peripherals: try a different USB port and test on another machine.
3. Check Device Manager for driver errors (yellow exclamation marks).
4. Update the device driver from the manufacturer's website.
5. Run built-in diagnostics (Dell SupportAssist, HP Support Assistant, or Apple Diagnostics).
6. If physically damaged or the issue persists, contact IT for a hardware assessment.
""",
    "software_issue": """\
## Software Issue — Suggested Resolution

**Likely cause:** Corrupt installation, missing dependencies, licence expiry, or permissions issue.

**Steps to resolve:**

1. Close the application completely (check the system tray) and reopen.
2. Run the application as Administrator (right-click → Run as administrator).
3. Check for available updates and install them.
4. Reinstall: uninstall from Control Panel, delete leftover app data, then reinstall.
5. Verify you have enough disk space (minimum 10 GB free).
6. Check that your software licence is still valid.
""",
    "network_issue": """\
## Network Issue — Suggested Resolution

**Likely cause:** DHCP lease failure, DNS misconfiguration, or physical connectivity issue.

**Steps to resolve:**

1. Check if other devices on the same network are affected.
2. Restart your network adapter: Device Manager → right-click adapter → Disable → Enable.
3. On Windows: run `ipconfig /release`, then `ipconfig /renew`, then `ipconfig /flushdns`.
4. Try connecting via Ethernet if you are on Wi-Fi.
5. Test DNS: open Command Prompt and run `nslookup google.com`.
6. Reboot your router/switch if you are at home.
""",
    "email_issue": """\
## Email / Communications Issue — Suggested Resolution

**Likely cause:** Outlook profile corruption, OST file corruption, or M365 service issue.

**Steps to resolve:**

1. Check the Microsoft 365 service health page for known outages.
2. Test Outlook Web Access (OWA) — if OWA works, the issue is with the desktop client.
3. Restart Outlook from the system tray.
4. Run Outlook in Safe Mode: Win+R → `outlook.exe /safe` → Enter.
5. Create a new Outlook profile: Control Panel → Mail → Show Profiles → Add.
6. For Teams issues: clear the Teams cache and reinstall.
""",
    "access_request": """\
## Access Request — Next Steps

**Your access request has been received.**

1. An approval email will be sent to your manager at the address provided.
2. Your manager has **48 hours** to approve or decline the request.
3. Once approved, IT will provision access within **1 business day**.
4. You will receive a confirmation email when access has been granted.
5. For urgent access, reply to this ticket with "URGENT" and provide business justification.
""",
    "procurement_request": """\
## Procurement Request — Next Steps

**Your purchase request has been received.**

1. An approval request will be sent to your approving manager.
2. Upon approval, IT Procurement will raise a Purchase Order (PO).
3. Standard delivery: **5–10 business days** for in-stock items.
4. Status updates will be emailed at each stage: Approved → PO Raised → Dispatched → Delivered.
""",
    "onboarding_setup": """\
## Onboarding Setup — What to Expect

**Your onboarding request has been received.**

1. **Account creation**: Your M365 account and email will be created 1–2 days before start date.
2. **Device provisioning**: Your laptop/desktop will be imaged and configured before day one.
3. **Day-one**: IT will walk you through logging in, MFA setup, and VPN connection.
4. **Access**: All requested system access will be provisioned based on your manager's approvals.
5. **Follow-up**: IT will check in on day 3 to address any outstanding issues.
""",
    "generic_incident": """\
## IT Incident — Suggested Resolution

**Likely cause:** Based on your description, this may be a software, network, or configuration issue.

**Steps to resolve:**

1. Restart the affected application or service.
2. Reboot your device if the issue persists after restarting the application.
3. Check if other users are affected — if so, this may be an infrastructure issue.
4. Note any error messages or codes and include them in your follow-up.
5. Check the IT status page for known incidents.
""",
}


def generate_response_template(form_result: Any) -> str:
    """Rule-based template response — used when the browser WebGPU model is unavailable."""
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
