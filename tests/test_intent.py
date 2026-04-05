import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from intent.classifier import detect_intent, get_intro_message


class TestDetectIntent:
    # --- vpn ---
    def test_vpn_cisco(self):
        assert detect_intent("My Cisco AnyConnect won't connect") == "vpn"

    def test_vpn_wireguard(self):
        assert detect_intent("WireGuard tunnel keeps dropping") == "vpn"

    def test_vpn_remote(self):
        assert detect_intent("I can't access remote resources from home") == "vpn"

    # --- account ---
    def test_account_password(self):
        assert detect_intent("I forgot my password and need a reset") == "account"

    def test_account_locked(self):
        assert detect_intent("My account is locked after too many attempts") == "account"

    def test_account_mfa(self):
        assert detect_intent("MFA is not working for my login") == "account"

    # --- hardware ---
    def test_hardware_laptop(self):
        assert detect_intent("My laptop screen is flickering") == "hardware"

    def test_hardware_keyboard(self):
        assert detect_intent("The keyboard on my device stopped working") == "hardware"

    def test_hardware_printer(self):
        assert detect_intent("The printer in the office won't print") == "hardware"

    # --- software ---
    def test_software_install(self):
        assert detect_intent("I need to install a new application") == "software"

    def test_software_crash(self):
        assert detect_intent("The app keeps crashing with error code 0x80") == "software"

    def test_software_license(self):
        assert detect_intent("My software license has expired") == "software"

    # --- network ---
    def test_network_wifi(self):
        assert detect_intent("WiFi connection is very slow today") == "network"

    def test_network_no_internet(self):
        assert detect_intent("I have no internet connection at my desk") == "network"

    def test_network_dns(self):
        assert detect_intent("DNS resolution is failing for internal sites") == "network"

    # --- email ---
    def test_email_outlook(self):
        assert detect_intent("Outlook is not syncing my mailbox") == "email"

    def test_email_calendar(self):
        assert detect_intent("My calendar is not showing meeting invites") == "email"

    def test_email_teams(self):
        assert detect_intent("Teams calls keep disconnecting") == "email"

    # --- access ---
    def test_access_permission(self):
        assert detect_intent("I need permission to access the shared drive") == "access"

    def test_access_folder(self):
        assert detect_intent("Can't access the folder on the file server") == "access"

    def test_access_read_only(self):
        assert detect_intent("I only have read only access but need write access") == "access"

    # --- procurement ---
    def test_procurement_order(self):
        assert detect_intent("I need to order a new laptop for my team") == "procurement"

    def test_procurement_purchase(self):
        assert detect_intent("I want to purchase new equipment for my team") == "procurement"

    def test_procurement_quote(self):
        assert detect_intent("Can you get a quote for new equipment?") == "procurement"

    # --- onboarding ---
    def test_onboarding_new_joiner(self):
        assert detect_intent("I'm a new joiner and need my setup done") == "onboarding"

    def test_onboarding_first_day(self):
        assert detect_intent("It's my first day and I need to get started") == "onboarding"

    def test_onboarding_new_employee(self):
        assert detect_intent("We have a new employee joining on Monday") == "onboarding"

    # --- fallback ---
    def test_fallback_generic(self):
        assert detect_intent("Something is wrong I don't know what") == "generic_incident"

    def test_fallback_empty(self):
        assert detect_intent("") == "generic_incident"

    def test_fallback_gibberish(self):
        assert detect_intent("xyzzy foobar qux baz") == "generic_incident"

    # --- case insensitivity ---
    def test_case_insensitive_upper(self):
        assert detect_intent("VPN IS NOT WORKING") == "vpn"

    def test_case_insensitive_mixed(self):
        assert detect_intent("My Password Was RESET") == "account"

    def test_case_insensitive_title(self):
        assert detect_intent("Outlook Calendar Sync Issue") == "email"


class TestGetIntroMessage:
    def test_vpn_intro(self):
        msg = get_intro_message("vpn")
        assert "VPN" in msg or "vpn" in msg.lower()

    def test_generic_fallback_intro(self):
        msg = get_intro_message("unknown_intent")
        assert isinstance(msg, str) and len(msg) > 0

    def test_all_intents_have_intro(self):
        intents = [
            "vpn", "account", "hardware", "software", "network",
            "email", "access", "procurement", "onboarding", "generic_incident",
        ]
        for intent in intents:
            msg = get_intro_message(intent)
            assert isinstance(msg, str) and len(msg) > 0, f"Missing intro for {intent}"
