import logging
from typing import Callable

from forms import (
    vpn,
    account,
    hardware,
    software,
    network,
    email_comms,
    access,
    procurement,
    onboarding,
    generic_incident,
)

logger = logging.getLogger(__name__)

FORM_MAP: dict[str, Callable[[], str]] = {
    "vpn": vpn.build,
    "account": account.build,
    "hardware": hardware.build,
    "software": software.build,
    "network": network.build,
    "email": email_comms.build,
    "access": access.build,
    "procurement": procurement.build,
    "onboarding": onboarding.build,
    "generic_incident": generic_incident.build,
}


def dispatch_form(intent: str) -> str:
    """Return the HTML form for the given intent. Returns '' for greeting/chitchat."""
    if intent == "greeting":
        return ""
    builder = FORM_MAP.get(intent, FORM_MAP["generic_incident"])
    logger.debug("Dispatching form for intent: %s", intent)
    return builder()
