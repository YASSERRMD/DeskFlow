import logging

logger = logging.getLogger(__name__)

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
    "vpn": "I'll help you fix your VPN issue. Please fill in the details below:",
    "account": "I'll help you resolve your account issue. Please fill in the details below:",
    "hardware": "I'll help you with your hardware problem. Please fill in the details below:",
    "software": "I'll help you with your software issue. Please fill in the details below:",
    "network": "I'll help you troubleshoot your network problem. Please fill in the details below:",
    "email": "I'll help you with your email or communications issue. Please fill in the details below:",
    "access": "I'll help you with your access request. Please fill in the details below:",
    "procurement": "I'll help you submit a procurement request. Please fill in the details below:",
    "onboarding": "I'll help you get set up as a new joiner. Please fill in the details below:",
    "generic_incident": "I'll log your IT issue. Please fill in the details below:",
}


def detect_intent(message: str) -> str:
    """Score each intent by keyword matches and return the highest-scoring one."""
    lowered = message.lower()
    scores: dict[str, int] = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        if intent == "generic_incident":
            continue
        score = 0
        for kw in keywords:
            if kw in lowered:
                score += 1
        scores[intent] = score

    best_intent = max(scores, key=lambda k: scores[k])
    if scores[best_intent] == 0:
        logger.debug("No keyword match found, falling back to generic_incident")
        return "generic_incident"

    logger.debug("Detected intent: %s (score=%d)", best_intent, scores[best_intent])
    return best_intent


def get_intro_message(intent: str) -> str:
    """Return a friendly one-liner intro for the given intent."""
    return _INTRO_MESSAGES.get(intent, _INTRO_MESSAGES["generic_incident"])
