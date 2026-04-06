import logging
import re

logger = logging.getLogger(__name__)

# Words that indicate a greeting or chitchat — no IT issue, no form needed.
_GREETING_PATTERNS = re.compile(
    r"^\s*(hi+|hey+|hello+|howdy|yo+|sup|good (morning|afternoon|evening)|"
    r"thanks?|thank you|cheers|bye|goodbye|ok|okay|cool|great|sure|got it|noted)\s*[!?.]*\s*$",
    re.IGNORECASE,
)

INTENT_KEYWORDS: dict[str, list[str]] = {
    "vpn": [
        "vpn", "remote", "tunnel", "connect remotely", "cisco anyconnect",
        "wireguard", "openvpn", "remote access",
    ],
    "account": [
        "password", "locked", "login", "reset", "access denied",
        "sign in", "forgot", "credentials", "mfa", "2fa", "account",
    ],
    "hardware": [
        "laptop", "keyboard", "mouse", "monitor", "printer",
        "screen", "device", "battery", "charger", "headset", "webcam",
    ],
    "software": [
        "install", "app", "software", "crash", "update", "license",
        "application", "error code", "not opening", "uninstall",
    ],
    "network": [
        "internet", "wifi", "slow", "network", "connection",
        "no internet", "packet loss", "latency", "dns", "ethernet",
    ],
    "email": [
        "email", "outlook", "calendar", "teams", "mailbox",
        "meeting", "distribution list", "signature", "spam",
    ],
    "access": [
        "permission", "folder", "drive", "share", "access",
        "shared drive", "read only", "write access", "file server",
    ],
    "procurement": [
        "order", "request", "new laptop", "equipment",
        "purchase", "budget", "quote", "hardware request",
    ],
    "onboarding": [
        "new joiner", "joined", "first day", "setup",
        "onboard", "new employee", "getting started",
    ],
    "generic_incident": [],
}

_INTRO_MESSAGES: dict[str, str] = {
    "greeting": "Hey! I'm DeskFlow, your IT support assistant. What can I help you with today?",
    "vpn": "Sure, let's sort out your VPN. Fill in the quick form below and I'll get you a fix:",
    "account": "No worries — account issues are quick to fix. Tell me a bit more:",
    "hardware": "Got it, let's look at your hardware problem. A few details please:",
    "software": "Happy to help with that software issue. Just a few quick questions:",
    "network": "Let's get your connection sorted. Fill in the details below:",
    "email": "I'll help you with your email or comms issue. Quick form below:",
    "access": "Access request noted. Fill in the details and I'll get it moving:",
    "procurement": "Let's get your purchase request submitted. Fill in the form:",
    "onboarding": "Welcome! Let's get you set up. Fill in the onboarding form below:",
    "generic_incident": "I'm on it. Fill in the details below and I'll pull up the best steps for you:",
}


def detect_intent(message: str) -> str:
    """
    Return the best-matching intent for a user message.
    Returns 'greeting' for small talk so no form is shown.
    Falls back to 'generic_incident' when keywords match but intent is unclear.
    """
    stripped = message.strip()

    # Greetings / chitchat — no form needed
    if _GREETING_PATTERNS.match(stripped):
        return "greeting"

    lowered = stripped.lower()
    scores: dict[str, int] = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        if intent == "generic_incident":
            continue
        scores[intent] = sum(1 for kw in keywords if kw in lowered)

    best_intent = max(scores, key=lambda k: scores[k])
    if scores[best_intent] == 0:
        # Short messages with no keyword match are likely greetings / vague queries
        if len(stripped.split()) <= 4:
            return "greeting"
        logger.debug("No keyword match, falling back to generic_incident")
        return "generic_incident"

    logger.debug("Detected intent: %s (score=%d)", best_intent, scores[best_intent])
    return best_intent


def get_intro_message(intent: str) -> str:
    return _INTRO_MESSAGES.get(intent, _INTRO_MESSAGES["generic_incident"])
